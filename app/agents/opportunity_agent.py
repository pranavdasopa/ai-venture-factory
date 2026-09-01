class OpportunityAgent:

    def __init__(self):

        self.opportunities = [

            {
                "id": "ai-internship-001",
                "title": "AI / ML Internship",
                "company": "Technology Startup",
                "type": "Internship",
                "skills": [
                    "Python",
                    "AI",
                    "Machine Learning"
                ],
                "location": "Remote",
                "url": ""
            },

            {
                "id": "software-internship-001",
                "title": "Software Engineering Internship",
                "company": "Technology Company",
                "type": "Internship",
                "skills": [
                    "Python",
                    "C++",
                    "DSA"
                ],
                "location": "India",
                "url": ""
            },

            {
                "id": "ai-hackathon-001",
                "title": "AI Hackathon",
                "company": "Developer Community",
                "type": "Hackathon",
                "skills": [
                    "AI",
                    "Python"
                ],
                "location": "Online",
                "url": ""
            },

            {
                "id": "ml-program-001",
                "title": "Machine Learning Program",
                "company": "Education Platform",
                "type": "Program",
                "skills": [
                    "Python",
                    "ML",
                    "Data Science"
                ],
                "location": "Online",
                "url": ""
            }
        ]


    def search(self, query=""):

        query = str(query).lower().strip()

        if not query:

            return self.opportunities

        terms = query.split()

        results = []

        for opportunity in self.opportunities:

            searchable = (
                opportunity["title"]
                + " "
                + opportunity["company"]
                + " "
                + opportunity["type"]
                + " "
                + " ".join(
                    opportunity["skills"]
                )
                + " "
                + opportunity["location"]
            ).lower()

            score = 0

            for term in terms:

                if term in searchable:

                    score += 1

            if score > 0:

                result = dict(opportunity)

                result["match_score"] = score

                results.append(result)


        results.sort(
            key=lambda item: item["match_score"],
            reverse=True
        )

        return results


    def personalized_search(
        self,
        skills=None,
        goal=""
    ):

        skills = skills or []

        skills = [
            str(skill).strip()
            for skill in skills
            if str(skill).strip()
        ]

        goal = str(goal).strip()

        results = []

        for opportunity in self.opportunities:

            opportunity_skills = [
                skill.lower()
                for skill in opportunity["skills"]
            ]

            matched_skills = []

            for skill in skills:

                skill_lower = skill.lower()

                for opportunity_skill in opportunity_skills:

                    if (
                        skill_lower in opportunity_skill
                        or opportunity_skill in skill_lower
                    ):

                        if skill not in matched_skills:

                            matched_skills.append(
                                skill
                            )


            searchable = (
                opportunity["title"]
                + " "
                + opportunity["company"]
                + " "
                + opportunity["type"]
                + " "
                + " ".join(
                    opportunity["skills"]
                )
                + " "
                + opportunity["location"]
                + " "
                + goal
            ).lower()


            goal_matches = 0

            for word in goal.lower().split():

                if len(word) >= 3 and word in searchable:

                    goal_matches += 1


            score = (
                len(matched_skills) * 10
                + goal_matches
            )


            result = dict(opportunity)

            result["match_score"] = score

            result["matched_skills"] = matched_skills

            results.append(result)


        results.sort(
            key=lambda item: item["match_score"],
            reverse=True
        )

        return results