# -*- coding: utf-8 -*-
import argparse
from modules.dependency_resolver.engine import DependencyResolverModule

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    res = DependencyResolverModule().run()
    result = res["result"]

    print("=" * 80)
    print("206.4 DEPENDENCY RESOLVER TAMAMLANDI")
    print("=" * 80)
    print("Score    : " + str(result["score"]) + " / 100")
    print("Decision : " + str(result["decision"]))
    print("Risk     : " + str(result["risk"]))
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["output"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
