import trio

from bush_trip_generator.mission import load_mission
from trio import Path


# TODO: image path : check if ok with slash instead of backslash
# TODO: formatting the xml => beautiful soup

async def main():
    mission = await load_mission(Path(__file__).parent.parent /
                                 'bush_trips' / 'sources' / 'example_mission_pack' / 'example_mission_1')
    await (Path(__file__).parent.parent / 'tmp' / 'example_mission_1.xml').write_text(mission.dump())


if __name__ == '__main__':
    trio.run(main)
