## ChaiOS – POS app

Flutter app with inventory, sales, reports, and credit (Udar).

### Build
- Android debug APK: `flutter build apk --debug`
- Android release AAB: `flutter build appbundle`

### Run
- `flutter run -d <deviceId>`

### Features
- Inventory: add/edit items with stock and pricing
- Sales: select items, payment step (Cash/UPI/Credit), share/print bill
- Credit (Udar): create manual credit, add payment, reminders, mark paid
- Reports: period summary, charts, export CSV/PDF
- Settings: onboarding, license check, PIN/biometric lock, encrypted backup/restore, export logs

### Dev notes
- Local backend is optional; app uses Hive for storage
- API_BASE_URL may be set via `--dart-define`, default localhost:8080 for dev
