import io
import json
import math
import unittest
from kural_skills import KuralSkills, SkillRequest, SkillResult, DryRunBackend, GatewayBackend
from kural_skills.catalog import CATALOG, BASE_DIRECTIONS, GESTURES
from kural_skills.cli import Dispatcher, serve, main

class FakeGateway:
    """Contract test double, not a live robot or installed DIMOS gateway."""
    def __init__(self):
        self.records = {}; self.calls = []; self.cancel_state = "cancelled"
        self.throw = None; self.finish = False
    def capabilities(self):
        return {"protocol":"kural.skills.gateway.v1","runtime_integrated":True,
                "namespace":"test_only","skills":list(CATALOG)}
    def submit(self,payload):
        self.calls.append(("submit",payload))
        self.records[payload["operation_id"]] = payload
        if self.throw == "submit": raise TimeoutError("transport")
        return self.reply(payload,"running")
    def reply(self,payload,state):
        record = self.records.get(payload["operation_id"])
        return {"operation_id":payload["operation_id"],"skill":record["request"]["skill"] if record else "stop",
                "state":state,"reason":"test-only response"}
    def status(self,payload):
        self.calls.append(("status",payload))
        if self.throw == "status": raise TimeoutError("transport")
        return self.reply(payload,"command_finished" if self.finish else "running")
    def cancel(self,payload):
        self.calls.append(("cancel",payload))
        if self.throw == "cancel": raise TimeoutError("transport")
        return self.reply(payload,self.cancel_state)
    def stop(self,payload):
        self.calls.append(("stop",payload))
        if self.throw == "stop": raise TimeoutError("transport")
        return self.reply(payload,"cancel_requested")

class CatalogTests(unittest.TestCase):
    def test_all_eighteen_skills_validate_and_dry_run(self):
        self.assertEqual(len(CATALOG),18)
        robot = KuralSkills()
        for name in CATALOG:
            with self.subTest(name=name):
                result = robot.call(name)
                self.assertEqual(result.state,"dry_run")
                self.assertFalse(result.motion_verified)
                self.assertFalse(result.stop_confirmed)
                self.assertEqual(result.request["skill"],name)
    def test_direction_vectors(self):
        for name,direction in BASE_DIRECTIONS.items():
            with self.subTest(name=name):
                command = SkillRequest.create(name).command
                self.assertEqual(command["linear"],[direction[0]*.1,direction[1]*.1,0.])
                self.assertEqual(command["angular"],[0.,0.,direction[2]*.3])
                self.assertEqual(command["stream"],"nav_cmd_vel")
    def test_reverse_is_explicit_heading_yaw_not_car_wheel_angle(self):
        self.assertEqual(SkillRequest.create("steer_back_left").command["angular"][2],.3)
        self.assertEqual(SkillRequest.create("steer_back_right").command["angular"][2],-.3)
        self.assertLess(SkillRequest.create("steer_back_left").command["linear"][0],0)
    def test_lift_preserves_existing_actions(self):
        self.assertEqual(SkillRequest.create("lift_up").command["body"],{"kind":"actions","actions":["liftUp"]})
        self.assertEqual(SkillRequest.create("lift_down").command["body"],{"kind":"actions","actions":["liftDown"]})
    def test_gestures_names_only_no_duplicate_keyframes(self):
        for name in GESTURES:
            self.assertEqual(SkillRequest.create(name).command["body"],{"kind":"gesture","name":name})
    def test_invalid_parameters(self):
        for bad in (0,-1,True,False,float("nan"),float("inf"),"1",11,None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):SkillRequest.create("move_forward",duration_s=bad)
        for bad in (0,-.1,.21,True,float("nan")):
            with self.assertRaises(ValueError):SkillRequest.create("move_forward",speed_m_s=bad)
        with self.assertRaises(ValueError):SkillRequest.create("wave",timeout_s=31)
        with self.assertRaises(ValueError):SkillRequest.create("turn_left",yaw_rate_rad_s=.51)
        with self.assertRaises(ValueError):SkillRequest.create("missing")
        with self.assertRaises(ValueError):SkillRequest.create("wave",speed_m_s=.1)
        with self.assertRaises(ValueError):SkillRequest.create("lift_up",height_m=.5)
    def test_linear_norm_bound(self):
        with self.assertRaises(ValueError):SkillRequest.create("base_velocity",vx_m_s=.2,vy_m_s=.2)
        command = SkillRequest.create("base_velocity",vx_m_s=.12,vy_m_s=.16,yaw_rate_rad_s=-.5).command
        self.assertEqual(command["linear"],[.12,.16,0.])
    def test_schemas_and_copies(self):
        robot = KuralSkills(); definitions = robot.list_skills()
        self.assertEqual(len(robot.tools()),18)
        for item in definitions:
            self.assertFalse(item["parameters"]["additionalProperties"])
            self.assertEqual(set(item["parameters"]["properties"]),set(SkillRequest.create(item["name"]).parameters))
        item = robot.describe("move_forward");item["parameters"]["properties"]["duration_s"]["maximum"] = 999
        self.assertEqual(robot.describe("move_forward")["parameters"]["properties"]["duration_s"]["maximum"],10)
    def test_no_physical_claims(self):
        with self.assertRaises(ValueError):SkillResult("id","wave","gesture_finished","test",motion_verified=True)
        with self.assertRaises(ValueError):SkillResult("id","wave","cancelled","test",stop_confirmed=True)

class PythonApiTests(unittest.TestCase):
    def test_families(self):
        robot=KuralSkills()
        methods = [robot.base.forward,robot.base.backward,robot.base.left,robot.base.right,
            robot.base.steer_left,robot.base.steer_right,robot.base.steer_back_left,robot.base.steer_back_right,
            robot.base.turn_left,robot.base.turn_right,robot.base.velocity,robot.lift.up,robot.lift.down,
            robot.gestures.home,robot.gestures.wave,robot.gestures.point,robot.gestures.inspect,robot.gestures.stow]
        self.assertEqual({method().skill for method in methods},set(CATALOG))
    def test_context_closes(self):
        with KuralSkills() as robot:self.assertEqual(robot.base.forward().state,"dry_run")
        with self.assertRaises(RuntimeError):robot.start("wave")
    def test_dryrun_unknown_status(self):
        with self.assertRaises(ValueError):DryRunBackend().status("missing")
    def test_invalid_gesture(self):
        with self.assertRaises(ValueError):KuralSkills().gestures.run("made_up")

class GatewayContractTests(unittest.TestCase):
    def setUp(self):
        self.gateway=FakeGateway(); self.backend=GatewayBackend(self.gateway);self.robot=KuralSkills(self.backend)
    def test_no_second_active_command(self):
        action=self.robot.start("move_forward")
        self.assertEqual(action.status().state,"running")
        blocked=self.robot.start("lift_up")
        self.assertEqual(blocked.status().state,"blocked")
        self.assertEqual(sum(name=="submit" for name,_ in self.gateway.calls),1)
        self.assertEqual(action.cancel().state,"cancelled")
        self.assertEqual(self.robot.start("lift_up").status().state,"running")
    def test_deadline_cancel_not_rpc_completion(self):
        action=self.robot.start("move_forward");self.gateway.cancel_state="cancel_requested"
        result=action.wait(timeout_s=.001)
        self.assertEqual(result.state,"outcome_unknown")
        self.assertTrue(any(name=="cancel" for name,_ in self.gateway.calls))
        # Even if status recovers to running, no second command can be admitted.
        self.assertEqual(self.robot.start("move_right").status().state,"blocked")
    def test_timeout_does_not_retry_submit(self):
        self.gateway.throw="submit"
        action=self.robot.start("wave")
        self.assertEqual(action._result.state,"outcome_unknown")
        self.assertEqual(self.robot.start("wave").status().state,"blocked")
        self.assertEqual(sum(name=="submit" for name,_ in self.gateway.calls),1)
    def test_status_and_cancel_timeout_unknown(self):
        action=self.robot.start("move_forward");self.gateway.throw="status"
        self.assertEqual(action.status().state,"outcome_unknown")
        self.gateway.throw="cancel"
        self.assertEqual(action.cancel().state,"outcome_unknown")
    def test_stop_does_not_resume(self):
        self.robot.start("wave");result=self.robot.stop()
        self.assertEqual(result.state,"cancel_requested")
        self.assertFalse(result.stop_confirmed)
        self.assertEqual([name for name,_ in self.gateway.calls],["submit","stop"])
    def test_gateway_declares_integration_and_supported_skills(self):
        class Disconnected(FakeGateway):
            def capabilities(self):return {"protocol":"kural.skills.gateway.v1","runtime_integrated":False}
        with self.assertRaises(ValueError):GatewayBackend(Disconnected())
        self.backend.skills=frozenset()
        self.assertEqual(self.robot.call("wave").state,"blocked")
        self.assertEqual(len(self.gateway.calls),0)
    def test_malformed_ack_is_unknown(self):
        self.gateway.submit=lambda payload:{"operation_id":"wrong","skill":"wave","state":"running"}
        self.assertEqual(self.robot.start("wave")._result.state,"outcome_unknown")
    def test_exact_payload_no_heartbeat_or_controller_writes(self):
        action=self.robot.start("steer_back_right",duration_s=.5,speed_m_s=.12,yaw_rate_rad_s=.25)
        name,payload=self.gateway.calls[0]
        self.assertEqual(name,"submit")
        self.assertEqual(set(payload),{"client_id","operation_id","request"})
        self.assertEqual(payload["operation_id"],action.operation_id)
        self.assertEqual(payload["request"]["command"]["angular"],[0.,0.,-.25])
    def test_finished_is_not_verified_motion(self):
        action=self.robot.start("move_forward");self.gateway.finish=True
        result=action.wait(timeout_s=.1)
        self.assertEqual(result.state,"command_finished");self.assertFalse(result.motion_verified)
    def test_custom_backend_exception_unknown_and_no_retry(self):
        class Broken(DryRunBackend):
            def submit(self,request):raise RuntimeError("test transport failure")
            def status(self,operation_id):raise RuntimeError("test status failure")
        robot=KuralSkills(Broken())
        self.assertEqual(robot.start("wave")._result.state,"outcome_unknown")
        self.assertEqual(robot.start("wave").status().state,"blocked")

class JsonInterfaceTests(unittest.TestCase):
    def test_json_lines_success_error_and_continue(self):
        incoming=io.StringIO('not json\n'+json.dumps({"id":1,"method":"call","skill":"move_forward","params":{"duration_s":.5}})+'\n'+
            json.dumps({"id":2,"method":"call","skill":"lift_up","params":{"duration_s":False}})+'\n'+
            json.dumps({"id":3,"method":"list"})+'\n')
        outgoing=io.StringIO();serve(KuralSkills(),incoming,outgoing)
        rows=[json.loads(line) for line in outgoing.getvalue().splitlines()]
        self.assertEqual([row["ok"] for row in rows],[False,True,False,True])
        self.assertEqual(rows[1]["result"]["state"],"dry_run")
        self.assertEqual(rows[1]["id"],1)
        self.assertEqual(len(rows[3]["result"]),18)
    def test_agent_actions_and_unknown_fields(self):
        dispatcher=Dispatcher(KuralSkills());r=dispatcher.dispatch({"method":"start","skill":"wave"})
        self.assertEqual(dispatcher.dispatch({"method":"status","operation_id":r["operation_id"]})["state"],"dry_run")
        with self.assertRaises(ValueError):dispatcher.dispatch({"method":"start","skill":"wave","resume":True})
        with self.assertRaises(ValueError):dispatcher.dispatch({"method":"status","operation_id":"missing"})
        with self.assertRaises(ValueError):dispatcher.dispatch({"method":"call","skill":"wave","params":[]})
    def test_invalid_id_and_nonstandard_json(self):
        outgoing=io.StringIO()
        serve(KuralSkills(),io.StringIO('{"id":{},"method":"list"}\n{"id":NaN,"method":"list"}\n'),outgoing)
        self.assertTrue(all(not json.loads(row)["ok"] for row in outgoing.getvalue().splitlines()))
    def test_bounded_registry(self):
        dispatcher=Dispatcher(KuralSkills())
        for _ in range(300):dispatcher.dispatch({"method":"start","skill":"wave"})
        self.assertLessEqual(len(dispatcher.actions),128)

class RobustnessRegressionTests(unittest.TestCase):
    def test_huge_integer_rejected_without_session_crash(self):
        huge=10**400
        with self.assertRaises(ValueError):SkillRequest.create("move_forward",duration_s=huge)
        with self.assertRaises(ValueError):SkillRequest.create("base_velocity",vx_m_s=-huge)
        incoming=io.StringIO(json.dumps({"id":1,"method":"call","skill":"lift_up","params":{"duration_s":huge}})+"\n"+
                            json.dumps({"id":2,"method":"list"})+"\n")
        outgoing=io.StringIO();serve(KuralSkills(),incoming,outgoing)
        rows=[json.loads(row) for row in outgoing.getvalue().splitlines()]
        self.assertEqual([row["ok"] for row in rows],[False,True])
    def test_dryrun_backend_history_really_bounded(self):
        backend=DryRunBackend(max_records=8);dispatcher=Dispatcher(KuralSkills(backend))
        for _ in range(500):dispatcher.dispatch({"method":"start","skill":"wave"})
        self.assertEqual(len(backend._results),8)
        self.assertLessEqual(len(dispatcher.actions),128)
    def test_gateway_history_evicts_only_known_terminal(self):
        gateway=FakeGateway();backend=GatewayBackend(gateway,max_records=2)
        a=backend.submit(SkillRequest.create("wave"));gateway.finish=True
        self.assertEqual(backend.status(a.operation_id).state,"command_finished")
        b=backend.submit(SkillRequest.create("wave"))
        c=backend.submit(SkillRequest.create("wave"))
        self.assertEqual(c.state,"running")
        self.assertNotIn(a.operation_id,backend._requests)
        self.assertIn(b.operation_id,backend._requests)
        self.assertEqual(len(backend._requests),2)
        self.assertEqual(len(backend._states),2)
    def test_gateway_does_not_evict_unknown_to_admit_new_motion(self):
        gateway=FakeGateway();gateway.throw="submit";backend=GatewayBackend(gateway,max_records=1)
        a=backend.submit(SkillRequest.create("wave"))
        self.assertEqual(a.state,"outcome_unknown")
        b=backend.submit(SkillRequest.create("move_forward"))
        self.assertEqual(b.state,"blocked")
        self.assertIn(a.operation_id,backend._requests)
        self.assertEqual(sum(name=="submit" for name,_ in gateway.calls),1)
    def test_cache_limit_is_validated(self):
        for bad in (0,-1,True,1.5,5000):
            with self.assertRaises(ValueError):DryRunBackend(max_records=bad)
            with self.assertRaises(ValueError):GatewayBackend(FakeGateway(),max_records=bad)

class ReviewRegressionTests(unittest.TestCase):
    def test_pruning_uses_one_snapshot_keeps_unknown_recovering_action(self):
        gateway=FakeGateway();backend=GatewayBackend(gateway);robot=KuralSkills(backend)
        dispatcher=Dispatcher(robot);first=dispatcher.dispatch({"method":"start","skill":"wave"})
        original=first["operation_id"];gateway.throw="status"
        for _ in range(127):dispatcher.dispatch({"method":"start","skill":"wave"})
        self.assertEqual(len(dispatcher.actions),128)
        calls=[]
        def uncertain_then_running(payload):
            calls.append(payload)
            return gateway.reply(payload,"outcome_unknown" if len(calls)==1 else "running")
        gateway.status=uncertain_then_running
        dispatcher.dispatch({"method":"start","skill":"wave"})
        self.assertIn(original,dispatcher.actions)
        self.assertEqual(dispatcher.dispatch({"method":"cancel","operation_id":original})["state"],"cancelled")
    def test_non_json_gateway_evidence_becomes_unknown_session_continues(self):
        gateway=FakeGateway()
        for method in ("submit","status"):
            original=getattr(gateway,method)
            def broken(payload,original=original):
                result=original(payload);result["evidence"]={"invalid":float("nan")};return result
            setattr(gateway,method,broken)
        robot=KuralSkills(GatewayBackend(gateway));incoming=io.StringIO(
            '{"id":1,"method":"start","skill":"wave"}\n{"id":2,"method":"list"}\n')
        outgoing=io.StringIO();serve(robot,incoming,outgoing)
        rows=[json.loads(row) for row in outgoing.getvalue().splitlines()]
        self.assertEqual(rows[0]["result"]["state"],"outcome_unknown")
        self.assertTrue(rows[1]["ok"]);self.assertEqual(len(rows[1]["result"]),18)
    def test_injected_backend_result_revalidated_after_mutation(self):
        class Corrupt(DryRunBackend):
            def submit(self,request):
                result=super().submit(request);result.evidence["bad"]=object();return result
        robot=KuralSkills(Corrupt())
        self.assertEqual(robot.start("wave")._result.state,"outcome_unknown")
        self.assertEqual(robot.start("move_forward").status().state,"blocked")
    def test_result_metadata_must_be_finite_json_objects(self):
        for bad in ({"x":float("nan")},{"x":float("inf")},{"x":object()},[],None):
            with self.assertRaises(ValueError):SkillResult("id","wave","running","test",evidence=bad)
        original={"valid":[1,2]};result=SkillResult("id","wave","running","test",evidence=original)
        original["valid"].append(3)
        self.assertEqual(result.evidence,{"valid":[1,2]})
        output=result.as_dict();output["evidence"]["valid"].append(4)
        self.assertEqual(result.evidence,{"valid":[1,2]})

class CanonicalSnapshotTests(unittest.TestCase):
    def test_submission_can_mutate_request_then_fail_without_poisoning_fallback(self):
        class Mutating(DryRunBackend):
            def submit(self,request):
                request.command["linear"][0]=float("nan")
                raise TimeoutError("transport after mutation")
        robot=KuralSkills(Mutating());action=robot.start("move_forward")
        self.assertEqual(action._result.state,"outcome_unknown")
        self.assertEqual(action._result.request["command"]["linear"],[.1,0.,0.])
        self.assertEqual(robot.start("move_right").status().state,"blocked")
    def test_retained_result_mutation_does_not_poison_status_or_cancel_fallback(self):
        class Mutating:
            def submit(self,request):
                self.result=SkillResult("owned","move_forward","running","test",request.as_dict())
                return self.result
            def status(self,operation_id):
                self.result.request["command"]["linear"][0]=float("nan")
                return self.result
            def cancel(self,operation_id):return self.result
            def stop(self):return SkillResult("stop-id","stop","cancel_requested","test")
        robot=KuralSkills(Mutating());action=robot.start("move_forward")
        result=action.status();self.assertEqual(result.state,"outcome_unknown")
        self.assertEqual(result.request["command"]["linear"],[.1,0.,0.])
        self.assertEqual(action.cancel().state,"outcome_unknown")
    def test_request_serialization_does_not_expose_mutable_command(self):
        request=SkillRequest.create("move_forward");output=request.as_dict()
        output["command"]["linear"][0]=float("nan")
        self.assertEqual(request.command["linear"],[.1,0.,0.])

if __name__ == "__main__":unittest.main()
