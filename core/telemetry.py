import json
import os
import datetime

class Telemetry:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.log_file = "/home/ubuntu/AI-Code-Reviewer/telemetry_log.json"
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def log_event(self, event_type, data):
        if not self.enabled:
            return
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                logs.append(event)
                f.seek(0)
                json.dump(logs, f, indent=4)
        except:
            pass

    def get_stats(self):
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
                return {
                    "total_events": len(logs),
                    "reviews_performed": len([e for e in logs if e['event_type'] == 'code_review']),
                    "errors": len([e for e in logs if e['event_type'] == 'error'])
                }
        except:
            return {"total_events": 0, "reviews_performed": 0, "errors": 0}
