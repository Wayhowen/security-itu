import asyncio
import sys

from assignment2.party import Party


def main(keyword_arguments):
    party = Party(**keyword_arguments)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(party.work())


if __name__ == '__main__':
    required_keywords = ["name", "starting"]
    arguments = sys.argv[1:]
    keyword_arguments = {sel[0]: sel[1] for sel in [el.split("=") for el in sys.argv[1:]]}

    for required_keyword in required_keywords:
        if required_keyword not in keyword_arguments:
            sys.exit(f'Please provide the "{required_keyword}" argument.')

    main(keyword_arguments)
