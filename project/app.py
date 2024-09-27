from flask import Flask, request, jsonify, render_template
import pandas as pd
from neo4j import GraphDatabase

app = Flask(__name__)

# Corrected path to the dataset
dataset_path = 'data/sample_candidates_data.csv'

# Load the dataset
df = pd.read_csv(dataset_path)

# Neo4j connection details
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "Csk2024@"

# Initialize the Neo4j driver
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Define the home route that renders the index.html
@app.route('/')
def home():
    return render_template('index.html')

# Define the search route
@app.route('/search', methods=['GET'])
def search_candidates():
    query = request.args.get('query')
    filtered_data = df[df['Name'].str.contains(query, case=False, na=False)]

    # Add candidates to Neo4j database
    with driver.session() as session:
        for _, row in filtered_data.iterrows():
            session.run(
                """
                MERGE (c:Candidate {name: $name, email: $email, college: $college, year: $year, degree: $degree, skills: $skills})
                """,
                name=row['Name'], email=row['Email'], college=row['College'],
                year=row['Year of Passout'], degree=row['Degree'], skills=row['Skills']
            )

    # Return the filtered data as JSON response
    return jsonify(filtered_data.to_dict(orient='records'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
