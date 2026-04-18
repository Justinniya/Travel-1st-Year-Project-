from flask import Flask, render_template, abort, request, jsonify
import smtplib, os, uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# ─── Email Configuration ────────────────────────────────────────────────────
# Replace with your Gmail address and App Password, OR set as environment vars.
#
# How to get a Gmail App Password:
#   1. Enable 2-Step Verification on your Google account
#   2. Google Account → Security → App Passwords → Mail → Generate
#   3. Paste the 16-character password as SMTP_PASSWORD below (no spaces)
#
SMTP_EMAIL    = os.environ.get('SMTP_EMAIL',    'justindelavega00@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'hmma ptvb bxze qmxy')
SMTP_HOST     = 'smtp.gmail.com'
SMTP_PORT     = 587

print(f'[Email config] SMTP_EMAIL={SMTP_EMAIL}, SMTP_HOST={SMTP_HOST}, SMTP_PORT={SMTP_PORT}, SMTP_PASSWORD={"(set)" if SMTP_PASSWORD and SMTP_PASSWORD != "your_email_password" else "(not set)"}')
# ─────────────────────────────────────────────────────────────────────────────

DESTINATIONS = [
    'boracay', 'iloilocity', 'capiz', 'bacolodcity',
    'aklan', 'negrosoccidental', 'antique', 'guimaras', 'iloilo-province'
]

CATEGORY_LABELS = {
    'attractions':    'Attraction',
    'activities':     'Activity',
    'food':           'Restaurant',
    'events':         'Event',
    'accommodations': 'Accommodation',
}


# ─── Email HTML Builder ──────────────────────────────────────────────────────
def build_ticket_email(ticket_num, name, place, category, destination, schedule, guests, addons):
    category_label = CATEGORY_LABELS.get(category, category.replace('-', ' ').title())
    dest_display   = destination.replace('-', ' ').title()
    booked_on      = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    guest_word     = 'person' if str(guests) == '1' else 'people'

    addons_block = ''
    if addons:
        rows = ''.join(
            f'<tr>'
            f'  <td style="padding:5px 0;font-size:14px;color:#555;">{a["name"]}</td>'
            f'  <td style="padding:5px 0;text-align:right;font-size:14px;color:#555;">{a["price"]}</td>'
            f'</tr>'
            for a in addons
        )
        addons_block = f'''
        <tr>
          <td colspan="2" style="padding-top:20px;padding-bottom:4px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:2px;
                        text-transform:uppercase;color:#5ab0c8;">Add-Ons</div>
          </td>
        </tr>
        {rows}
        '''

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f0f2f5;
             font-family:'Helvetica Neue',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#f0f2f5;padding:48px 0;">
    <tr><td align="center">

      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:20px;
                    overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,.10);">

        <!-- Header -->
        <tr>
          <td style="background:#1c1c1e;padding:38px 44px;text-align:center;">
            <div style="font-size:11px;font-weight:800;letter-spacing:4px;
                        text-transform:uppercase;color:#a8d8ea;margin-bottom:10px;">
              Western Visayas Travel
            </div>
            <div style="font-size:30px;font-weight:900;letter-spacing:5px;
                        text-transform:uppercase;color:#fff;">
              Booking Ticket
            </div>
          </td>
        </tr>

        <!-- Ticket number band -->
        <tr>
          <td style="background:#a8d8ea;padding:22px 44px;text-align:center;">
            <div style="font-size:10px;font-weight:800;letter-spacing:2.5px;
                        text-transform:uppercase;color:#1c3a4a;margin-bottom:6px;">
              Ticket Number
            </div>
            <div style="font-size:28px;font-weight:900;letter-spacing:6px;color:#1c3a4a;">
              {ticket_num}
            </div>
          </td>
        </tr>

        <!-- Greeting -->
        <tr>
          <td style="padding:36px 44px 8px;">
            <p style="margin:0;font-size:15px;color:#444;line-height:1.7;">
              Hi <strong>{name}</strong>, your booking is confirmed! &#127881;<br/>
              Here are your reservation details for
              <strong>{dest_display}, Western Visayas</strong>.
            </p>
          </td>
        </tr>

        <!-- Details -->
        <tr>
          <td style="padding:8px 44px 36px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border-top:1px solid #eee;margin-top:20px;">

              <tr>
                <td colspan="2" style="padding:16px 0;border-bottom:1px solid #eee;">
                  <div style="font-size:10px;font-weight:800;letter-spacing:2px;
                              text-transform:uppercase;color:#a8d8ea;margin-bottom:5px;">Place</div>
                  <div style="font-size:18px;font-weight:700;color:#1c1c1e;">{place}</div>
                </td>
              </tr>

              <tr>
                <td colspan="2" style="padding:14px 0;border-bottom:1px solid #eee;">
                  <div style="font-size:10px;font-weight:800;letter-spacing:2px;
                              text-transform:uppercase;color:#a8d8ea;margin-bottom:5px;">Category</div>
                  <div style="font-size:15px;color:#444;">{category_label}</div>
                </td>
              </tr>

              <tr>
                <td colspan="2" style="padding:14px 0;border-bottom:1px solid #eee;">
                  <div style="font-size:10px;font-weight:800;letter-spacing:2px;
                              text-transform:uppercase;color:#a8d8ea;margin-bottom:5px;">Destination</div>
                  <div style="font-size:15px;color:#444;">{dest_display}, Western Visayas, Philippines</div>
                </td>
              </tr>

              <tr>
                <td style="padding:14px 0;border-bottom:1px solid #eee;width:50%;">
                  <div style="font-size:10px;font-weight:800;letter-spacing:2px;
                              text-transform:uppercase;color:#a8d8ea;margin-bottom:5px;">Schedule</div>
                  <div style="font-size:15px;color:#444;">{schedule}</div>
                </td>
                <td style="padding:14px 24px;border-bottom:1px solid #eee;width:50%;">
                  <div style="font-size:10px;font-weight:800;letter-spacing:2px;
                              text-transform:uppercase;color:#a8d8ea;margin-bottom:5px;">Guests</div>
                  <div style="font-size:15px;color:#444;">{guests} {guest_word}</div>
                </td>
              </tr>

              {addons_block}

            </table>

            <p style="margin:24px 0 0;font-size:12px;color:#bbb;text-align:center;">
              Booked on {booked_on}
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8f8f8;padding:24px 44px;
                     text-align:center;border-top:1px solid #eee;">
            <p style="margin:0;font-size:11px;color:#aaa;line-height:1.8;">
              Thank you for booking with <strong>Western Visayas Travel</strong>.<br/>
              Please present this ticket on your scheduled date.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_ticket_email(to_email, subject, html_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'Western Visayas Travel <{SMTP_EMAIL}>'
    msg['To']      = to_email
    msg.attach(MIMEText(html_body, 'html'))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())


# ─── Routes ─────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/<destination>')
def destination_page(destination):
    if destination not in DESTINATIONS:
        abort(404)
    return render_template('destination_page.html', destination=destination)

@app.route('/<destination>/detail')
def detail_page(destination):
    if destination not in DESTINATIONS:
        abort(404)
    return render_template('detail_page.html', destination=destination)

# Legacy redirect — keep old /boracay/detail working
@app.route('/boracay/detail')
def boracay_detail_legacy():
    return render_template('detail_page.html', destination='boracay')


@app.route('/api/book', methods=['POST'])
def api_book():
    data        = request.get_json()
    name        = data.get('name', '').strip()
    email       = data.get('email', '').strip()
    place       = data.get('place', '').strip()
    category    = data.get('category', '').strip()
    destination = data.get('destination', '').strip()
    schedule    = data.get('schedule', '').strip()
    guests      = data.get('guests', '1').strip()
    addons      = data.get('addons', [])

    # Generate unique ticket number
    ticket_num = f"WV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # Send email (fail silently — booking always succeeds on the frontend)
    email_sent = False
    if email and SMTP_EMAIL != 'your_email@gmail.com':
        try:
            html_body = build_ticket_email(
                ticket_num, name, place, category,
                destination, schedule, guests, addons
            )
            send_ticket_email(
                email,
                f'\U0001f3ab Your Booking – {place} | {ticket_num}',
                html_body
            )
            email_sent = True
        except Exception as e:
            print(f'[Email error] {e}')

    return jsonify({'success': True, 'ticket': ticket_num, 'email_sent': email_sent})


if __name__ == '__main__':
    app.run(debug=True, port=3300)
