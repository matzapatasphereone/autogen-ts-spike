import subprocess

# JavaScript code
js_code = """
function add(x, y) {
    return x + y;
}

console.log(add(2, 3));
"""
# js_code = "function reverseString(str) {\n  return str.split('').reverse().join('');\n}\n\nconst inputString = 'hello world';\nconst reversedString = reverseString(inputString);\nreversedString;"

# Execute JavaScript code using Node.js
result = subprocess.run(["node", "-e", js_code], capture_output=True, text=True)
print(result.stdout.strip())  # Output: 5

print(result.stderr.strip())
print(result.returncode)
