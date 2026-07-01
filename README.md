# Roblox Cloud PC Control Panel

This is a deployable control panel for a Roblox cloud PC. It does not stream Roblox by itself; it gives you a clean page for opening remote-access tools, checking a cloud machine, and optionally sending start/stop commands that you configure on the server.

## Run locally

```bash
cd roblox-cloud-phone
copy .env.example .env
npm start
```

Then open:

```text
http://127.0.0.1:4317
```

## Static hosting

The files can also be hosted as a static site on GitHub Pages or Cloudflare Pages. Static mode keeps the launcher UI and saved links, but disables backend status and start/stop commands because static hosts do not run `server.js`.

Upload these files to the static host:

- `index.html`
- `styles.css`
- `app.js`
- `.nojekyll`

No build command is required.

## What makes it work when your PC is off

The control panel must run on an always-on host, and Roblox must run on a separate always-on or startable cloud machine.

Typical setup:

1. Rent a Windows cloud PC or GPU VM.
2. Install Roblox on that cloud PC.
3. Install one remote access tool: Chrome Remote Desktop, Parsec, or Sunshine/Moonlight.
4. Deploy this control panel on the same VM, another small VPS, Render, Railway, Fly.io, or similar.
5. Set `.env` values for the remote access URL and optional cloud start/stop commands.

## Optional machine control

Start/stop commands are disabled unless all required values are configured:

- `CLOUD_CONTROL_TOKEN`
- `START_COMMAND`
- `STOP_COMMAND`

The browser sends only the token. Cloud credentials stay on the server where the command runs.

Example command shapes:

```env
START_COMMAND=aws ec2 start-instances --instance-ids i-xxxxxxxx
STOP_COMMAND=aws ec2 stop-instances --instance-ids i-xxxxxxxx
STATUS_COMMAND=aws ec2 describe-instance-status --instance-ids i-xxxxxxxx --include-all-instances
```

## Safety notes

- Do not put your Roblox password in this app.
- Use Roblox 2FA.
- Use the official Roblox login inside Roblox or the remote-access session.
- Keep the control panel behind a strong token if you enable power controls.
