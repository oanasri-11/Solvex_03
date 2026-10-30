p = "Backend/app/services/assignment_service.py"
s = open(p, encoding="utf-8").read()

# Find first is_doctor_assigned and first assert_doctor_has_access
idx1 = s.find("def is_doctor_assigned")
idx2 = s.find("def assert_doctor_has_access", idx1)
# Find second is_doctor_assigned
idx3 = s.find("def is_doctor_assigned", idx2 + 1)
print("First is_doctor_assigned at:", idx1)
print("First assert at:", idx2)
print("Second is_doctor_assigned at:", idx3)

# Keep: first is_doctor_assigned through first assert, then add clean versions
first_part = s[:idx3].rstrip() + "\n"

# Also remove the 'import re' that's in the file (leftover)
first_part = first_part.replace('import re\n', '')

# Write deduplicated version
open(p, "w", encoding="utf-8").write(first_part)
print("Deduplicated. Total lines:", len(first_part.split("\n")))
