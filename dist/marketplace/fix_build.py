import sys

with open('dist/marketplace/build_marketplace.py', 'r') as f:
    code = f.read()

code = code.replace("lines.join('\n')", "lines.join('\\n')")

with open('dist/marketplace/build_marketplace.py', 'w') as f:
    f.write(code)

print("Fixed build_marketplace.py")
