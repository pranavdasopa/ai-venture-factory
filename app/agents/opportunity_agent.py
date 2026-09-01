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

        query = str(query).lower().strip()

        if not query:
            return self.opportunities

        results = []

        for opportunity in self.opportunities:

            searchable = " ".join([
                opportunity["title"],
                opportunity["company"],
                opportunity["type"],
                " ".join(opportunity["skills"]),
                opportunity["location"]
            ]).lower()

            if query in searchable:
                results.append(opportunity)

        return results


    def personalized_search(self, skills=None, goal=""):

        skills = skills or []

        if isinstance(skills, str):
            skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

        user_skills = {
            str(skill).lower().strip()
            for skill in skills
            if str(skill).strip()
        }

        goal_words = set(
            str(goal).lower().replace("/", " ").split()
        )

        ranked = []

        for opportunity in self.opportunities:

            opportunity_skills = {
                str(skill).lower().strip()
                for skill in opportunity["skills"]
            }

            skill_matches = (
                user_skills & opportunity_skills
            )

            searchable = " ".join([
                opportunity["title"],
                opportunity["company"],
                opportunity["type"],
                " ".join(opportunity["skills"]),
                opportunity["location"]
            ]).lower()

            goal_matches = sum(
                1 for word in goal_words
                if len(word) >= 3 and word in searchable
            )

            score = (
                len(skill_matches) * 10
                + goal_matches * 2
            )

            ranked.append({
                **opportunity,
                "match_score": score,
                "matched_skills": sorted(skill_matches)
            })

        ranked.sort(
            key=lambda item: item["match_score"],
            reverse=True
        )

        return ranked