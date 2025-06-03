def generate_pick():
    try:
        from scraper.betonline import fetch_betonline_nba_lines
        lines = fetch_betonline_nba_lines()
        if not lines:
            return None

        pick = lines[0]  # First available pick
        return (
            f"🏀 NBA\n"
            f"{pick['player']} – {pick['team']}\n"
            f"📆 {pick['date']}\n"
            f"🎯 {pick['book']}: {pick['line']}\n"
            f"📈 Confidence: {pick.get('confidence', 'N/A')} | Diff: {pick.get('diff', 'N/A')}"
        )
    except Exception as e:
        print("❌ generate_pick error:", str(e))
        return None
