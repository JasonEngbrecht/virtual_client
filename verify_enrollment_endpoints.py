"""
Verify enrollment endpoints are registered in the API
"""

from backend.app import app

print("Checking registered routes...\n")

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        routes.append((route.path, list(route.methods)))

# Filter for enrollment-related routes
enrollment_routes = [
    (path, methods) for path, methods in routes 
    if 'roster' in path or 'enroll' in path
]

print("Enrollment endpoints found:")
for path, methods in enrollment_routes:
    for method in methods:
        if method != 'HEAD':  # Skip HEAD methods
            print(f"  {method:6} {path}")

# Also check section endpoints
print("\nSection management endpoints:")
section_routes = [
    (path, methods) for path, methods in routes 
    if '/sections' in path and 'roster' not in path and 'enroll' not in path
]
for path, methods in section_routes[:5]:  # Limit output
    for method in methods:
        if method != 'HEAD':
            print(f"  {method:6} {path}")

# Expected enrollment endpoints
expected = [
    ("GET", "/api/teacher/sections/{section_id}/roster"),
    ("POST", "/api/teacher/sections/{section_id}/enroll"),
    ("DELETE", "/api/teacher/sections/{section_id}/enroll/{student_id}")
]

print("\nVerifying expected endpoints...")
for method, path in expected:
    found = any(
        path.replace("{section_id}", "{" + "section_id" + "}").replace("{student_id}", "{" + "student_id" + "}") in route_path 
        and method in route_methods
        for route_path, route_methods in enrollment_routes
    )
    status = "✓" if found else "✗"
    print(f"  {status} {method} {path}")

print("\n✅ Endpoint verification complete!")
