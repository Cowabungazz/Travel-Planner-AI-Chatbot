# Travel-Planner-AI-Chatbot
Personalised travel recommendations -> planning -> booking

# Backend Demo
1. cd to rag
2. poetry install 
3. poetry run generate
4. poetry run dev -> tables will be created in postgres (main.py)
5. http://localhost:8000/docs
6. postman environment
7. postman collection

# Context Storage and Retrieval: PINECONE for vector database
How to decide which goes where?
Define only for postgres for persistent storage and temporary storage, if not defined all will go to either vector database or temporary vector embeddings

Flow:
Postgres for persistent storage will always be used as context
Temporary storage will always be used for context
Vector database will be queried for relevant context
Temporary vector embeddings will be queried for relevant context

Updates to context storage (else add):
Update defined keys in persistent storage if spotted (need to ownself implement with external package)
Else goes to either vector database or temporary vector embeddings and replaces the vector

User message:
-> persistent storage: using tool
-> temporary storage: using tool
-> persistent embeddings: using tool
-> temporary embeddings: using tool

Chat response:
-> always temporary embeddings: using tool

# Register A User:
1️⃣ Checks if the username already exists.
If it does, an error is returned: "Username already exists"
2️⃣ Encrypts the password.
This ensures passwords are securely stored.
3️⃣ Creates a new user account.
Stores the username and hashed password in the database.
4️⃣ Saves the new user.
Ensures the user can log in later.
5️⃣ Sends a confirmation message.

Response: { "message": "User registered successfully" }

<img width="1481" height="264" alt="image" src="https://github.com/user-attachments/assets/b4d80c53-e6a6-40b7-8797-d5e4601a54ed" />

# Logging in (Obtain Access Token):
1️⃣ Checks if the username exists.
If not, an error is returned: "Invalid username or password".
2️⃣ Verifies the password.
If incorrect, the same error is returned.
3️⃣ Creates an access token.
This token allows the user to access the system securely.
4️⃣ Sends the token back.
Response: { "access_token": "<TOKEN_HERE>", "token_type": "bearer" }
<img width="1477" height="285" alt="image" src="https://github.com/user-attachments/assets/419eaf6e-27d5-4f25-aa63-d8a5df056201" />

# Create A New Chat Session for User:
1️⃣ Verifies the user token.
If invalid, an error is returned: "Invalid authentication".
2️⃣ Creates a new chat session.
The session is linked to the user in the database.
3️⃣ Saves the chat session.
Ensures the user can continue the conversation later.
4️⃣ Sends the session ID back.
Response: { "session_id": "<new_session_id>" }
<img width="1483" height="258" alt="image" src="https://github.com/user-attachments/assets/205f7a74-fbce-4024-bb78-61dbcfb6bc71" />

# Sending Message In Chat Session:
1️⃣ Verifies the user token.
If invalid, an error is returned: "Invalid authentication".
2️⃣ Fetches all chat sessions linked to the user.
Retrieves session data from the database.
3️⃣ Formats and sends the data.

Response: { "sessions": [ { "session_id": 1, "created_at": "2025-02-19T12:00:00" } ] }

<img width="1476" height="948" alt="image" src="https://github.com/user-attachments/assets/ac9eb075-d28c-4cf5-b26f-870c9940bea8" />

# Get All Chat Sessions of User:
1️⃣ Verifies the user token.
If invalid, an error is returned: "Invalid authentication".
2️⃣ Checks if the session exists and belongs to the user.
If not, an error is returned: "Chat session not found".
3️⃣ Fetches messages in order.
Retrieves all messages linked to the session.
4️⃣ Sends messages back.

Response: { "session_id": 1, "messages": [ { "id": 1, "role": "user", "content": "Hello" } ] }

<img width="1480" height="366" alt="image" src="https://github.com/user-attachments/assets/363595b3-bdaf-43df-9b53-82ea3b39a136" />

# Get All Messages from A Chat Session of A User:
1️⃣ Verifies the user token.
If invalid, an error is returned: "Invalid authentication".
2️⃣ Checks if the session exists and belongs to the user.
If not, an error is returned: "Invalid session ID".
3️⃣ Stores the message in the chat session. 
Saves message content, sender role, and timestamp.
4️⃣ Refer to Context Storage and Retrieval**
Retrieves context, stores context, proceeds to next step.
5️⃣ User message is sent to external LLM to evaluate intent.
The chatbot decides whether to make a tool call based on intent detected.
Available Tools:
query_engine ()
recommend_products ( country: string, city: string, type: Optional[string] )
query_engine () formats a response based on .pdf, .xslx, .csv, .doc, .txt documents vectorized in the backend.
recommend_products () formats a response based on products returned from BMG API, filtered by city, country, and type in order of highest to lowest priority.
Response is saved in database
Refer to Context Storage and Retrieval**
5️⃣ Sends back the message details based on the entire conversation history.

Response: {
  "id": "aTYTg72tpp5wmZAW",
  "createdAt": "Wed Feb 26 2025 23:25:43 GMT+0800 (Singapore Standard Time)",
  "role": "assistant",
  "content": "How can I assist you with your travel-related questions?",
  "annotations": [
    {
      "type": "sources",
      "data": {}
    }
  ],
  "revisionId": "32HEhK3GLGyzQaEP"
}

5️⃣ Sends back the message details with data fetched from the tool.

Response: {
  "id": "pEYkEtWqqo1tTkcR",
  "createdAt": "Wed Feb 26 2025 23:31:43 GMT+0800 (Singapore Standard Time)",
  "role": "assistant",
  "content": "- Japan 4G Pocket WiFi Rental (Japan Airport Pickup)\n- Tokyo Subway Ticket",
  "annotations": [
    {
      "type": "events",
      "data": {
        "title": "Calling tool: recommend_products with inputs: {\"country\":\"Japan\",\"city\":\"Tokyo\",\"type\":\"Activity\"}"
      }
    },
    {
      "type": "sources",
      "data": {
        "nodes": []
      }
    },
    {
      "type": "tools",
      "data": {
        "toolCall": {
          "id": null,
          "input": {
            "args": [],
            "kwargs": {
              "city": "Tokyo",
              "country": "Japan",
              "type": "Activity"
            }
          },
          "name": "recommend_products"
        },
        "toolOutput": {
          "isError": false,
          "output": {
            "products": [
              {
                "uuid": "6e3eeea2-a866-42f8-b84c-bb7549b765f9",
                "title": "Japan 4G Pocket WiFi Rental (Japan Airport Pickup) (Test)",
                "description": "Enjoy smooth connectivity during your visit to Japan. Enjoy unlimited WiFi access from four to seven days.",
                "highlights": "Experience fast internet speed and smooth connectivity. Pick up your pocket WiFi router at any of Japan's major airports.",
                "additionalInfo": "- You can collect and return the pocket WiFi router at the airport. For more details: ninjawifi.com/en/receive/airport"
              },
              {
                "uuid": "5be6279d-2770-4e4c-ac0b-3f13057e3703",
                "title": "Tokyo Subway Ticket",
                "description": "Make your way around the most popular things to do in Tokyo and get where you need to go quickly and easily.",
                "highlights": "Travel around Tokyo city fast and easy using the local subway. Enjoy extra value offers in over 350 locations in Tokyo.",
                "additionalInfo": "Child Policy:\r\n- Free of charge: Children under 6 (when accompanied by a paying adult)\r\nhttps://bit.ly/3SuBO8d (exchange method)"
              }
            ]
          }
        }
      }
    },
    {
      "type": "suggested_questions",
      "data": [
        "What are some popular tourist attractions in Tokyo?",
        "Can you suggest some local food to try in Tokyo?",
        "Are there any cultural experiences I shouldn't miss while in Tokyo?"
      ]
    }
  ],
  "revisionId": "cOBlDkfhsrdJtIli"
}

<img width="1478" height="415" alt="image" src="https://github.com/user-attachments/assets/0b31ca4f-4ec1-4330-b416-0aeb23dde0e6" />








