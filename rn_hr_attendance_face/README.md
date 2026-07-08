# HR Attendance Face Recognition

Commercial-grade face recognition attendance for Odoo 19 Community.

## Architecture

```
Browser (OWL Webcam)
        |
        v
Odoo Controller
        |
        v
Face Recognition Services
  - Detection
  - Embedding
  - Matching
  - Anti-spoof
        |
        v
Odoo HR Attendance
```

AI logic lives in `services/`. Models store profiles, logs, devices, and settings.

Embeddings (not match photos) are stored for scalable matching.

## Phase 1 (current)

- Installable module skeleton
- Security groups: Administrator, HR Manager, Attendance Officer, Employee, Readonly
- Models: Employee Face, Attendance Log, Camera, Device, Settings, Session, History
- Service stubs for detection, embedding, recognition, attendance, anti-spoof, camera, device, notifications, scheduler
- OWL dashboard and kiosk shells
- Controllers and API stubs
- Cron placeholders, demo data, skeleton tests

## Installation

1. Add `rn_hr_attendance_face` to the addons path.
2. Install optional AI packages from `requirements.txt` when moving to Phase 3+.
3. Update Apps and install **HR Attendance Face Recognition**.
4. Enable the feature under **Face Attendance > Configuration > Settings**.

## Dependencies

- Odoo apps: `hr`, `hr_attendance`
- Python: `numpy` (required). Optional later: `opencv-python`, `insightface`, `onnxruntime`, `cryptography`

## Roadmap

| Phase | Deliverable |
|-------|-------------|
| 1 | Skeleton (done) |
| 2 | Multi-angle face registration |
| 3 | Embedding generation and encrypted storage |
| 4 | OWL webcam kiosk with real-time recognition |
| 5 | Attendance and shift rules |
| 6 | Anti-spoofing |
| 7 | GPS, IP, device validation |
| 8 | Multi-camera / RTSP |
| 9 | Dashboard analytics and reports |
| 10 | REST API, jobs, tests, documentation |

## License

LGPL-3

## Support

info@armorait.com
