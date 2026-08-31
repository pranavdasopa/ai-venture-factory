class OpportunityAgent:

    def __init__(self):

        self.opportunities = [

            {
                "id": 1,
                "title": "AI / ML Internship",
                "company": "Technology Startup",
                "type": "Internship",
                "skills": ["Python", "AI", "Machine Learning"],
                "location": "Remote"
            },

            {
                "id": 2,
                "title": "Software Engineering Internship",
                "company": "Technology Company",
                "type": "Internship",
                "skills": ["Python", "C++", "DSA"],
                "location": "India"
            },

            {
                "id": 3,
                "title": "AI Hackathon",
                "company": "Developer Community",
                "type": "Hackathon",
                "skills": ["AI", "Python"],
                "location": "Online"
            },

            {
                "id": 4,
                "title": "Machine Learning Program",
                "company": "Education Platform",
                "type": "Program",
                "skills": ["Python", "ML", "Data Science"],
                "location": "Online"
            }
        ]


    def search(self, query=""):

        query = query.lower().strip()

        if not query:
            return self.opportunities

        results = []

        for opportunity in self.opportunities:

            searchable = (
                opportunity["title"]
                + " "
                + opportunity["company"]
                + " "
                + opportunity["type"]
                + " "
                + " ".join(opportunity["skills"])
                + " "
                + opportunity["location"]
            ).lower()

            if query in searchable:
                results.append(opportunity)

        return results


    def personalized_search(self, skills=None, goal=""):

        skills = skills or []

        query = " ".join(skills) + " " + goal

        return self.search(query)