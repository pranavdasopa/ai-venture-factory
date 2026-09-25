import argparse
from app.core.company_runtime import CompanyRuntime

def main():
    parser = argparse.ArgumentParser(description="AI Venture Factory company runtime")
    parser.add_argument("--once", action="store_true", help="Run one supervisor heartbeat")
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

    runtime = CompanyRuntime()
    print("AI VENTURE FACTORY")
    print("==================")
    print("COMPANY RUNTIME    ONLINE")
    print("AGENT REGISTRY     ONLINE")
    print("TASK SYSTEM        ONLINE")
    print("EVENT BUS          ONLINE")
    print("AUDIT SYSTEM       ONLINE")

    if args.once:
        print(runtime.status())
        return
    runtime.run_forever(args.interval)

if __name__ == "__main__":
    main()
