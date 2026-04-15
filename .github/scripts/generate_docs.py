    # Identifiera vilka mappar som ändrats (ignorera rot-filer och .github-mappen)
    folders = set()
    for f in files_changed:
        parts = f.split('/')
        # Ignorera filer i roten, filer i .github, och filer i mappar vars namn börjar med '.'
        if '/' in f and not any(part.startswith('.') for part in parts[:-1]):
            folders.add(os.path.dirname(f))