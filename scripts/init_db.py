from sqlalchemy.orm import Session
from db.session import get_engine
from db.models import Base, Source

def main():
    engine = get_engine()
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        def ensure(name, kind, homepage=None):
            if not s.query(Source).filter(Source.name == name).first():
                s.add(Source(name=name, kind=kind, homepage=homepage))

        ensure("PRNewswire RSS", "rss", "https://www.prnewswire.com/rss/")
        ensure("Manual", "manual", None)
        s.commit()

    print("DB initialized.")

if __name__ == "__main__":
    main()
