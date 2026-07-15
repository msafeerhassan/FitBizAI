def renderPage(title, bodyHtml):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FitBizAI - {title}</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            max-width: 900px;
            margin: 30px auto;
            padding: 0 16px;
            color: #1a1a1a;
        }}
        nav a {{
            margin-right: 14px;
            text-decoration: none;
            color: #2563eb;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/insights">Insights</a>
        <a href="/achievements">Achievements</a>
        <a href="/manage-logs">Manage Logs</a>
        <a href="/targets">Targets</a>
        <a href="/progress-photos">Progress Photos</a>
        <a href="/log/diet">Log Meal</a>
        <a href="/log/water">Log Water</a>
        <a href="/log/workout">Log Workout</a>
        <a href="/log/productivity">Log Work</a>
        <a href="/log/context">Add Context</a>
        <a href="/fortnightly">Fortnightly Report</a>
        <a href="/coach-chat">Chat with Coach</a>
        <a href="/signup">Sign Up</a>
    </nav>
    <hr>
    {bodyHtml}
</body>
</html>"""