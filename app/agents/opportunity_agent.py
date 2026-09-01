import requests


class OpportunityAgent:

    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self):

        self.demo_opportunities = [

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


    def _extract_skills(self, job):

        text = (
            str(job.get("title", "")) + " " +
            str(job.get("description", ""))
        ).lower()

        known_skills = [
            "python",
            "c++",
            "c",
            "java",
            "javascript",
            "typescript",
            "react",
            "node.js",
            "sql",
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "ai",
            "data science",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "git",
            "linux",
            "django",
            "flask",
            "fastapi",
            "tensorflow",
            "pytorch",
            "embedded systems",
            "verilog",
            "vlsi"
        ]

        found = []

        for skill in known_skills:

            if skill in text and skill not in found:

                found.append(skill)

        return found


    def fetch_live(self):

        try:

            response = requests.get(
                self.API_URL,
                params={
                    "page": 1
                },
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            jobs = data.get("data", [])

            results = []

            for job in jobs:

                title = job.get(
                    "title",
                    "Untitled position"
                )

                company = job.get(
                    "company_name",
                    "Unknown company"
                )

                location = job.get(
                    "location",
                    "Not specified"
                )

                description = job.get(
                    "description",
                    ""
                )

                url = job.get(
                    "url",
                    ""
                )

                remote = job.get(
                    "remote",
                    False
                )

                skills = self._extract_skills(job)

                results.append({

                    "id": job.get(
                        "slug",
                        url
                    ),

                    "title": title,

                    "company": company,

                    "type": "Remote" if remote else "Job",

                    "skills": skills,

                    "location": location,

                    "url": url,

                    "source": "Arbeitnow"

                })

            return results

        except Exception:

            return []


    def search(self, query=""):

        query = query.lower().strip()

        live_jobs = self.fetch_live()

        if not live_jobs:

            opportunities = self.demo_opportunities

        else:

            opportunities = live_jobs


        if not query:

            return opportunities


        results = []

        for opportunity in opportunities:

            searchable = (

                str(
                    opportunity.get("title", "")
                )
                + " "
                + str(
                    opportunity.get("company", "")
                )
                + " "
                + str(
                    opportunity.get("type", "")
                )
                + " "
                + " ".join(
                    opportunity.get("skills", [])
                )
                + " "
                + str(
                    opportunity.get("location", "")
                )

            ).lower()


            if query in searchable:

                results.append(
                    opportunity
                )

        return results


    def personalized_search(
        self,
        skills=None,
        goal=""
    ):

        skills = skills or []

        if isinstance(skills, str):

            skills = [
                item.strip()
                for item in skills.split(",")
                if item.strip()
            ]

        goal = str(goal or "").strip()

        live_jobs = self.fetch_live()

        if not live_jobs:

            opportunities = self.demo_opportunities

        else:

            opportunities = live_jobs


        user_terms = set()

        for skill in skills:

            user_terms.add(
                skill.lower().strip()
            )

        for word in goal.lower().split():

            if len(word) >= 3:

                user_terms.add(word)


        scored = []

        for opportunity in opportunities:

            searchable = (

                str(
                    opportunity.get("title", "")
                )
                + " "
                + str(
                    opportunity.get("company", "")
                )
                + " "
                + str(
                    opportunity.get("type", "")
                )
                + " "
                + " ".join(
                    opportunity.get("skills", [])
                )
                + " "
                + str(
                    opportunity.get("location", "")
                )

            ).lower()


            matched = []

            for term in user_terms:

                if term and term in searchable:

                    matched.append(term)


            score = 0

            if user_terms:

                score = round(
                    (
                        len(matched)
                        / len(user_terms)
                    ) * 100
                )


            item = dict(opportunity)

            item["match_score"] = score

            item["matched_skills"] = matched

            scored.append(item)


        scored.sort(
            key=lambda item: item["match_score"],
            reverse=True
        )

        return scored[:20]