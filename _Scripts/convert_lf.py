#!/usr/bin/env python3
"""Convert CRLF to LF in the export file."""
data = open(r'C:\EnvironmentPortfolio\.temp_export_clean.fi', 'rb').read()
data = data.replace(b'\r\n', b'\n')
open(r'C:\EnvironmentPortfolio\.temp_export_lf.fi', 'wb').write(data)
print(f"Converted: {len(data)} bytes written")
