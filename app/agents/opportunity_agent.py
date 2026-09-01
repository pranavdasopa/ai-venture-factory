import re
import requests


class OpportunityAgent:

    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self):
        self.demo_opportunities = [
            {
                "id": "demo-1",
                "title": "AI / ML Internship",
                "company": "Technology Startup",
                "type": "Internship",
                "skills": ["Python", "AI", "Machine Learning"],
                "location": "Remote",
                "url": "",
                "source": "Demo"
            },
            {
                "id": "demo-2",
                "title": "Software Engineering Internship",
                "company": "Technology Company",
                "type": "Internship",
                "skills": ["Python", "C++", "DSA"],
                "location": "India",
                "url": "",
                "source": "Demo"
            }
        ]

    def _clean_html(self, text):
        text = re.sub(r"<[^>]+>", " ", str(text or ""))
        return re.sub(r"\s+", " ", text).strip()

    def _extract_skills(self, job):
        text = (
            str(job.get("title", "")) + " " +
            self._clean_html(job.get("description", ""))
        ).lower()

        known_skills = [
            "python", "c++", "c", "java",
            "javascript", "typescript", "react",
            "node.js", "sql", "machine learning",
            "deep learning", "artificial intelligence",
            "ai", "data science", "docker",
            "kubernetes", "aws", "azure", "git",
            "linux", "django", "flask", "fastapi",
            "tensorflow", "pytorch",
            "embedded systems", "verilog", "vlsi",
            "cuda", "golang", "rust"
        ]

        return [
            skill for skill in known_skills
            if skill in text
        ]

    def fetch_live(self):
        try:
            response = requests.get(
                self.API_URL,
                params={"page": 1},
                timeout=15
            )

            response.raise_for_status()

            jobs = response.json().get("data", [])

            results = []

            for job in jobs:

                results.append({
                    "id": job.get("slug") or job.get("url"),
                    "title": job.get(
                        "title",
                        "Untitled position"
                    ),
                    "company": job.get(
                        "company_name",
                        "Unknown company"
                    ),
                    "type": (
                        "Remote"
                        if job.get("remote")
                        else "Job"
                    ),
                    "skills": self._extract_skills(job),
                    "location": job.get(
                        "location",
                        "Not specified"
                    ),
                    "url": job.get("url", ""),
                    "source": "Arbeitnow"
                })

            return results

        except Exception as error:
            print(
                "Live opportunity API unavailable:",
                error
            )
            return []

    def _get_opportunities(self):
        live = self.fetch_live()

        if live:
            return live

        return self.demo_opportunities

    def search(self, query=""):
        query = str(query or "").strip().lower()

        opportunities = self._get_opportunities()

        if not query:
            return opportunities[:20]

        results = []

        for opportunity in opportunities:

            searchable = " ".join([
                str(opportunity.get("title", "")),
                str(opportunity.get("company", "")),
                str(opportunity.get("type", "")),
                str(opportunity.get("location", "")),
                " ".join(opportunity.get("skills", []))
            ]).lower()

            if query in searchable:
                results.append(opportunity)

        return results[:20]

    def personalized_search(
        self,
        skills=None,
        goal=""
    ):
        skills = skills or []

        if isinstance(skills, str):
            skills = [
                x.strip()
                for x in skills.split(",")
                if x.strip()
            ]

        goal = str(goal or "").strip()

        opportunities = self._get_opportunities()

        user_terms = set(
            x.lower().strip()
            for x in skills
            if x.strip()
        )

        goal_words = re.findall(
            r"[a-zA-Z0-9+#.]+",
            goal.lower()
        )

        # Only use meaningful goal terms.
        ignored = {
            "the", "and", "for", "with",
            "from", "want", "become",
            "learn", "build", "work"
        }

        for word in goal_words:
            if len(word) >= 3 and word not in ignored:
                user_terms.add(word)

        scored = []

        for opportunity in opportunities:

            title = str(
                opportunity.get("title", "")
            ).lower()

            company = str(
                opportunity.get("company", "")
            ).lower()

            location = str(
                opportunity.get("location", "")
            ).lower()

            opportunity_skills = [
                x.lower()
                for x in opportunity.get(
                    "skills",
                    []
                )
            ]

            searchable = " ".join([
                title,
                company,
                location,
                " ".join(opportunity_skills)
            ])

            matched = []

            for term in user_terms:

                if (
                    term in opportunity_skills
                    or term in searchable
                ):
                    matched.append(term)

            # Skills receive more weight than generic
            # goal-word matches.
            skill_matches = sum(
                1
                for term in matched
                if term in opportunity_skills
            )

            generic_matches = len(matched) - skill_matches

            score = (
                skill_matches * 25
                + generic_matches * 8
            )

            score = min(score, 100)

            item = dict(opportunity)

            item["match_score"] = score
            item["matched_skills"] = matched

            scored.append(item)

        scored.sort(
            key=lambda x: x["match_score"],
            reverse=True
        )

        return scored[:20]