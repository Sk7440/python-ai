# python-ai

My work for the Python for AI course.

## Task 1.8: Business Helper Bot design

**Business:** Bright Future Tuition Centre (Johar Town, Lahore)

| # | Intent (what the user wants) | Keywords to look for | Reply |
|---|---|---|---|
| 1 | Complaint / problem (checked first) | late, complaint, refund, bad | Sorry about that. The centre manager will call you today. |
| 2 | Talk to a human | agent, human (exact) | Connecting you to a human... (ends chat) |
| 3 | Greeting | starts with hi / hello, or exactly salam | Hello {name}! How can I help you today? |
| 4 | Timings | timing, time, open | Classes run 3 pm to 8 pm, Monday to Saturday. |
| 5 | Fees | fee, price, cost | Monthly fee is 5,000 PKR per subject. |
| 6 | Subjects | subject, math, physics | We teach Maths, Physics, Chemistry and English for Matric and FSc. |
| 7 | Location | location, address, where | We are at Main Boulevard, Johar Town, Lahore. |
| 8 | Admission | admission, join, enroll | Admissions are open. Visit with your last result card. |
| - | Anything else (fallback) | none matched | Counted as unanswered; prints the AI prompt for Module 2. |