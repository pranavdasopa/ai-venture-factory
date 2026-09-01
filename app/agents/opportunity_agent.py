class OpportunityAgent:

    def __init__(self):

        self.opportunities = [

            {
                "id": 1,
                "title": "AI / ML Internship",
                "company": "Technology Startup",
                "type": "Internship",
                "skills": [
                    "Python",
                    "AI",
                    "Machine Learning"
                ],
                "location": "Remote",
                "description": "AI and machine learning internship opportunity.",
                "url": ""
            },

            {
                "id": 2,
                "title": "Software Engineering Internship",
                "company": "Technology Company",
                "type": "Internship",
                "skills": [
                    "Python",
                    "C++",
                    "DSA"
                ],
                "location": "India",
                "description": "Software engineering internship focused on programming and problem solving.",
                "url": ""
            },

            {
                "id": 3,
                "title": "AI Hackathon",
                "company": "Developer Community",
                "type": "Hackathon",
                "skills": [
                    "AI",
                    "Python"
                ],
                "location": "Online",
                "description": "Online hackathon for developers building AI projects.",
                "url": ""
            },

            {
                "id": 4,
                "title": "Machine Learning Program",
                "company": "Education Platform",
                "type": "Program",
                "skills": [
                    "Python",
                    "Machine Learning",
                    "Data Science"
                ],
                "location": "Online",
                "description": "Machine learning learning program.",
                "url": ""
            }

        ]


    # ======================================
    # NORMAL SEARCH
    # ======================================

    def search(self, query=""):

        query = str(
            query or ""
        ).lower().strip()


        if not query:

            return self.opportunities


        words = [
            word
            for word in query.split()
            if word
        ]


        results = []


        for opportunity in self.opportunities:

            searchable = " ".join([

                opportunity["title"],

                opportunity["company"],

                opportunity["type"],

                opportunity["location"],

                opportunity["description"],

                " ".join(
                    opportunity["skills"]
                )

            ]).lower()


            score = 0


            for word in words:

                if word in searchable:

                    score += 1


            if score > 0:

                result = dict(
                    opportunity
                )

                result["match_score"] = score

                result["matched_skills"] = []

                for skill in opportunity["skills"]:

                    if skill.lower() in query:

                        result[
                            "matched_skills"
                        ].append(skill)


                results.append(result)


        results.sort(
            key=lambda item:
                item.get(
                    "match_score",
                    0
                ),
            reverse=True
        )


        return results


    # ======================================
    # PERSONALIZED SEARCH
    # ======================================

    def personalized_search(
        self,
        skills=None,
        goal=""
    ):

        skills = skills or []

        goal = str(
            goal or ""
        ).lower().strip()


        normalized_skills = []


        for skill in skills:

            skill = str(
                skill
            ).strip().lower()


            if skill:

                normalized_skills.append(
                    skill
                )


        results = []


        for opportunity in self.opportunities:

            opportunity_skills = [

                skill.lower()

                for skill
                in opportunity["skills"]

            ]


            matched_skills = []


            for user_skill in normalized_skills:

                for opportunity_skill in opportunity_skills:

                    if (
                        user_skill
                        == opportunity_skill
                        or
                        user_skill
                        in opportunity_skill
                        or
                        opportunity_skill
                        in user_skill
                    ):

                        original_skill = next(
                            skill
                            for skill
                            in opportunity["skills"]
                            if skill.lower()
                            == opportunity_skill
                        )

                        if (
                            original_skill
                            not in matched_skills
                        ):

                            matched_skills.append(
                                original_skill
                            )


            goal_words = [

                word

                for word
                in goal.split()

                if len(word) > 2

            ]


            searchable = " ".join([

                opportunity["title"],

                opportunity["type"],

                opportunity["description"],

                opportunity["location"],

                " ".join(
                    opportunity["skills"]
                )

            ]).lower()


            goal_matches = 0


            for word in goal_words:

                if word in searchable:

                    goal_matches += 1


            skill_score = (
                len(matched_skills)
            )


            total_score = (
                skill_score * 3
                + goal_matches
            )


            if total_score > 0:

                result = dict(
                    opportunity
                )

                result[
                    "match_score"
                ] = total_score

                result[
                    "matched_skills"
                ] = matched_skills

                results.append(
                    result
                )


        results.sort(

            key=lambda item:
                item.get(
                    "match_score",
                    0
                ),

            reverse=True

        )


        return results