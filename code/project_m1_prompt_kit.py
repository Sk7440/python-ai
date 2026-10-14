print(f"""AI Prompt tool for a Business: Purpose of the tool is to provide exact use of AI through prompt which can be given to Claude or ChatGPT and other AI model,for business owners who want to use AI but don't know what to type or what is prompt.""")
 
# business details so every prompt is should be clear for AI model to suggest or guide in best way
business_name = input("your Business name: ")
business_type = input("What is your Business type : ")
city = input("Your City: ")
customers = input("Target Audience : ")

# type of input() is str,so that's why we use int( ) here to turns the str into a number
budget = int(input("Your Monthly budget in PKR : "))


# Header requirement complete
print(f"AI Prompt Kit for {business_name}")

# As per requirement prompts are ready each prompt have role,task,tone 
print("1.Marketing")
print(f"You are a social media marketer. Write a short Instagram post for {business_name}, "
      f"a {business_type} in {city}. Target only {customers}.Always in a Friendly tone, under 80 words, "
      f"exactly 1 call to action and familiar hashtags.")

print("3. Customer Service")
print(f"You are the manager of {business_name}, a {business_type} in {city}. "
      f"Write a polite or customer friendly reply to an unhappy customer whose order arrived late. "
      f"Apologise to customer, offer a discount to coustmer, keep it under 50 words.")

print("3. Growth")
print(f"You are a business AI consultant. Suggest 3 low-cost AI tools or ideas "
      f"a {business_type} in {city} can use to attract {customers}, "
      f"with a total budget of {budget} PKR per month.  give the cost also predict the future results for each. "
      f"Ask them,If you are not sure about a price.")


print("4. Automation")
print(f"You are a AI Automation Specialist. Suggest 2 to 5 AI Aoutomation ideas "
      f"a {business_type} in {city} can use to attract {customers}, "
      f"with a total budget of {budget} PKR per month. For each, give the cost also predict the outcomes. "
      f"Ask the most manual work which cause the waste of time e.g bill are manually generated, customer feedback is manually collected, etc.")