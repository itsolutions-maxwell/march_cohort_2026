import csv
import json
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

CSV_FILES = {
    "stays": DATA_DIR / "stays.csv",
    "users": DATA_DIR / "users.csv",
    "bookings": DATA_DIR / "bookings.csv",
}


def read_csv_records(name: str) -> list[dict[str, str]]:
    with CSV_FILES[name].open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv_records(name: str, records: list[dict[str, str]]) -> None:
    if not records:
        return

    fieldnames = list(records[0].keys())
    with CSV_FILES[name].open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def next_id(records: list[dict[str, str]], prefix: str, field_name: str) -> str:
    highest = 0
    for record in records:
        raw = str(record.get(field_name, "")).replace(prefix, "")
        try:
            value = int(raw)
            highest = max(highest, value)
        except ValueError:
            continue

    return f"{prefix}{highest + 1:03d}"


def nights_between(check_in: str, check_out: str) -> int:
    start = datetime.fromisoformat(check_in)
    end = datetime.fromisoformat(check_out)
    return (end - start).days


class StayFinderHandler(SimpleHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict | list) -> None:
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/stays":
            return self._send_json(200, read_csv_records("stays"))

        if path == "/api/users":
            return self._send_json(200, read_csv_records("users"))

        if path == "/api/bookings":
            return self._send_json(200, read_csv_records("bookings"))

        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/bookings":
            return self._send_json(404, {"error": "Route not found."})

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return self._send_json(400, {"error": "Invalid JSON body."})

        full_name = str(payload.get("fullName", "")).strip()
        email = str(payload.get("email", "")).strip().lower()
        stay_id = str(payload.get("stayId", "")).strip()
        check_in = str(payload.get("checkIn", "")).strip()
        check_out = str(payload.get("checkOut", "")).strip()
        guests_raw = payload.get("guests", "")

        if not all([full_name, email, stay_id, check_in, check_out, guests_raw]):
            return self._send_json(400, {"error": "Missing required booking fields."})

        try:
            guests = int(guests_raw)
        except (TypeError, ValueError):
            return self._send_json(400, {"error": "Guests must be a number."})

        stays = read_csv_records("stays")
        users = read_csv_records("users")
        bookings = read_csv_records("bookings")

        selected_stay = next((stay for stay in stays if stay.get("stay_id") == stay_id), None)
        if not selected_stay:
            return self._send_json(400, {"error": "Stay not found."})

        max_guests = int(selected_stay["guests"])
        if guests < 1 or guests > max_guests:
            return self._send_json(400, {"error": f"Guests must be between 1 and {max_guests}."})

        nights = nights_between(check_in, check_out)
        if nights <= 0:
            return self._send_json(400, {"error": "Check-out must be after check-in."})

        user = next((item for item in users if item.get("email", "").strip().lower() == email), None)
        if not user:
            user = {
                "user_id": next_id(users, "U", "user_id"),
                "full_name": full_name,
                "email": email,
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            users.append(user)
            write_csv_records("users", users)

        total_price = nights * float(selected_stay["price_per_night"])
        booking = {
            "booking_id": next_id(bookings, "B", "booking_id"),
            "user_id": user["user_id"],
            "stay_id": selected_stay["stay_id"],
            "check_in": check_in,
            "check_out": check_out,
            "guests": str(guests),
            "total_price": str(int(total_price)),
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        bookings.append(booking)
        write_csv_records("bookings", bookings)

        return self._send_json(
            201,
            {
                "booking": booking,
                "user": user,
                "stay": selected_stay,
                "totalPrice": int(total_price),
                "message": "Booking saved to bookings.csv.",
            },
        )


if __name__ == "__main__":
    port = 3000
    server = ThreadingHTTPServer(("127.0.0.1", port), StayFinderHandler)
    print(f"StayFinder is running on http://127.0.0.1:{port}")
    server.serve_forever()
