"""Human CLI and JSON-lines agent interface. Both default to dry-run only."""
import argparse
import json
import sys
from typing import TextIO
from .sdk import KuralSkills, Action

class Dispatcher:
    """One in-process client/session. No HTTP, robot connection, or implicit resume."""
    def __init__(self, robot: KuralSkills):
        self.robot = robot
        self.actions: dict[str,Action] = {}

    def dispatch(self, message: dict):
        if not isinstance(message,dict): raise ValueError("Request must be an object")
        method = message.get("method")
        fields = {"list":set(),"tools":set(),"describe":{"skill"},"call":{"skill","params"},
                  "start":{"skill","params"},"status":{"operation_id"},"cancel":{"operation_id"},"stop":set()}
        if not isinstance(method,str) or method not in fields: raise ValueError("Unknown method")
        if message.keys()-fields[method]-{"id","method"}: raise ValueError("Unexpected request fields")
        if method == "list": return self.robot.list_skills()
        if method == "tools": return self.robot.tools()
        if method == "describe": return self.robot.describe(message.get("skill"))
        if method == "stop": return self.robot.stop().as_dict()
        if method in ("call","start"):
            params = message.get("params",{})
            if not isinstance(params,dict): raise ValueError("params must be an object")
            # Avoid an unbounded agent-session operation registry. Never evict an
            # unknown/in-flight live action merely to admit a fresh command.
            if len(self.actions) >= 128:
                finished = []
                for key,value in self.actions.items():
                    snapshot = value.status()
                    if snapshot.terminal and snapshot.state != "outcome_unknown":
                        finished.append(key)
                for key in finished: del self.actions[key]
                if len(self.actions) >= 128: raise ValueError("Too many unresolved operations")
            action = self.robot.start(message.get("skill"),**params)
            self.actions[action.operation_id] = action
            return (action.wait() if method == "call" else action.status()).as_dict()
        operation_id = message.get("operation_id")
        if not isinstance(operation_id,str) or operation_id not in self.actions:
            raise ValueError("Unknown operation ID in this session")
        action = self.actions[operation_id]
        return (action.cancel() if method == "cancel" else action.status()).as_dict()

def serve(robot: KuralSkills, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout):
    """One JSON request and response per line; EOF closes the client via STOP.

    RPC-like wire format, not an MCP server. Host code may pass a reviewed backend;
    the installed CLI always passes the dry-run default.
    """
    dispatcher = Dispatcher(robot)
    try:
        for line in input_stream:
            request_id = None
            try:
                # Reject non-standard JSON infinities/NaN before dispatch.
                def reject(value): raise ValueError(f"Invalid JSON constant: {value}")
                message = json.loads(line,parse_constant=reject)
                if isinstance(message,dict):
                    request_id = message.get("id")
                    if request_id is not None and type(request_id) not in (str,int):
                        request_id = None
                        raise ValueError("id must be a string, integer, or null")
                response = {"id":request_id,"ok":True,"result":dispatcher.dispatch(message)}
                encoded = json.dumps(response,allow_nan=False)
            except (ValueError,TypeError,RuntimeError,OverflowError) as exc:
                response = {"id":request_id,"ok":False,"error":str(exc)}
                encoded = json.dumps(response,allow_nan=False)
            output_stream.write(encoded+"\n")
            output_stream.flush()
    finally:
        robot.close()

def main(argv=None):
    parser = argparse.ArgumentParser(description="Kural Phase 1 skills. CLI is dry-run only; it never moves the robot.")
    sub = parser.add_subparsers(dest="method",required=True)
    for name in ("list","tools","stop","serve"): sub.add_parser(name)
    describe = sub.add_parser("describe"); describe.add_argument("skill")
    call = sub.add_parser("call"); call.add_argument("skill");call.add_argument("--params",default="{}",help="JSON parameter object")
    args = parser.parse_args(argv)
    robot = KuralSkills()
    if args.method == "serve": serve(robot); return 0
    try:
        message = {"method":args.method}
        if hasattr(args,"skill"): message["skill"] = args.skill
        if hasattr(args,"params"): message["params"] = json.loads(args.params)
        result = Dispatcher(robot).dispatch(message)
        print(json.dumps({"ok":True,"backend":"dry_run","result":result},allow_nan=False))
        return 0
    except (ValueError,TypeError,RuntimeError) as exc:
        print(json.dumps({"ok":False,"backend":"dry_run","error":str(exc)}))
        return 2
    finally: robot.close()
