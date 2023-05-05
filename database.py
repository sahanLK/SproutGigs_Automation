from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

engine = create_engine('mysql+pymysql://root:@localhost/testing', echo=False)
conn = engine.connect()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)
    pwd = Column(String(255))
    device = Column(Integer, unique=True)


class LoginInfo(Base):
    __tablename__ = 'login_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(255))   # Email field
    ip = Column(String(255), unique=True)
    date = Column(DateTime)


class Earnings(Base):
    __tablename__ = 'earnings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, unique=True)
    tasks = Column(Integer)
    usd = Column(String(255))


# Relational tables starts from here


class BlogSite(Base):
    __tablename__ = 'blog_sites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255))

    jobs = relationship("Job", back_populates="blog")
    posts = relationship('BlogPost', back_populates="blog")
    ad_sites = relationship("AdSite", secondary="link_blog_site_ad_site")

    def __repr__(self):
        return f"<BlogSite: {self.domain}>"


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blog_id = Column(Integer, ForeignKey('blog_sites.id'))
    job_id = Column(String(255), unique=True)
    title = Column(String(500))

    blog = relationship("BlogSite", back_populates="jobs")
    instruction_items = relationship(
        "InstructionItem",
        secondary="link_job_instruction_item",
        back_populates="jobs")
    submission_items = relationship("SubmissionItem", back_populates="job")

    def __repr__(self):
        return f"<Job: {self.job_id}>"


class BlogPost(Base):
    __tablename__ = 'blog_posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blog_id = Column(Integer, ForeignKey('blog_sites.id'))
    url = Column(String(1000), unique=True)
    title = Column(String(500))
    body = Column(String(1000))
    last_used = Column(DateTime())

    blog = relationship("BlogSite", back_populates="posts")

    def __repr__(self):
        return f"<BlogPost: {self.title}>"


class AdSite(Base):
    __tablename__ = 'ad_sites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255), unique=True)
    adsense_url = Column(String(1000))
    first_url = Column(String(1000))

    pages = relationship("AdPage", back_populates="ad_site")
    blog_sites = relationship(
        "BlogSite",
        secondary="link_blog_site_ad_site",
        back_populates="ad_sites")


class AdPage(Base):
    __tablename__ = 'ad_pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_site_id = Column(Integer, ForeignKey("ad_sites.id"))
    url = Column(String(1000), unique=True)

    ad_site = relationship("AdSite", back_populates="pages")


class InstructionItem(Base):
    __tablename__ = 'instruction_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    text = Column(String(1000), unique=True)

    jobs = relationship(
        "Job",
        secondary="link_job_instruction_item",
        back_populates="instruction_items")


class SubmissionItem(Base):
    __tablename__ = 'submission_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    text = Column(String(1000))
    field_id = Column(String(50))  # The id of the submission textarea
    decision = Column(Integer())
    submitted_value = Column(String(1000))

    job = relationship("Job", back_populates="submission_items")
    choices = relationship("SubmissionItemChoice", back_populates="sub_item")

    def __repr__(self):
        return f"<SubmissionItem: {self.text}>"


class SubmissionItemChoice(Base):
    __tablename__ = 'submission_item_choices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_item_id = Column(Integer, ForeignKey('submission_items.id'))
    text = Column(String(2500))

    sub_item = relationship("SubmissionItem", back_populates="choices")


class LinkBlogSiteAdSite(Base):
    __tablename__ = 'link_blog_site_ad_site'

    blogsite_id = Column(Integer, ForeignKey('blog_sites.id'), primary_key=True)
    adsite_id = Column(Integer, ForeignKey('ad_sites.id'), primary_key=True)


class LinkJobInstructionItem(Base):
    __tablename__ = 'link_job_instruction_item'

    job_id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)
    ins_id = Column(Integer, ForeignKey('instruction_items.id'), primary_key=True)


def get_session():
    Session = sessionmaker()
    return Session(bind=engine)


def main():
    Base.metadata.create_all(engine)
    print("Database Ready")


if __name__ == "__main__":
    main()
