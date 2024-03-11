import subprocess

# Your TypeScript code
typescript_code = """
function reverseString(str: string): string {
    return str.split('').reverse().join('');
}

console.log(reverseString('hello'));
"""

# Write TypeScript code to a temporary file
with open("temp.ts", "w") as file:
    file.write(typescript_code)

# Compile TypeScript code to JavaScript
subprocess.run(["tsc", "temp.ts"])

# Execute generated JavaScript code
result = subprocess.run(["node", "temp.js"], capture_output=True, text=True)
print(result.stdout.strip())

# Clean up temporary files
subprocess.run(["rm", "temp.ts", "temp.js"])
