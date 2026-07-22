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
        .metric {{
            display: inline-block;
            margin-right: 24px;
        }}

        .metric .label {{
            font-size: 12px;
            color: #666;
        }}

        .metric .value {{
            font-size: 22px;
            font-weight: 600;
        }}

        .card {{
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
        }}

        input, textarea {{
            display: block;
            width: 100%;
            padding: 8px;
            margin: 6px 0 14px;
            box-sizing: border-box;
        }}

        button {{
            background: #2563eb;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
        }}
        .badge-earned {{
            background: #dcfce7;
            border: 1px solid #16a34a;
            border-radius: 8px;
            padding: 12px;
            margin: 6px;
        }}
        .badge-locked {{
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px;
            margin: 6px;
            color: #888;
        }}
        .chat-msg {{
            padding: 10px 14px;
            border-radius: 8px;
            margin: 8px 0;
            max-width: 80%;
        }}
        .chat-user {{
            background: #2563eb;
            color: white;
            margin-left: auto;
        }}
        .chat-assistant {{
            background: #f0f0f0;
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
        <a href="/logout">Log Out</a>
    </nav>
    <hr>
    {bodyHtml}
</body>
</html>"""