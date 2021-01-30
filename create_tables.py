import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    """
    Delete table if exists in order to be able to re-create it again
    """
    print('Drop all tables')
    for query in drop_table_queries:
        print('Executing query: ' + query + ' ')
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    Create dimensional and staging tables that have been defined in sql_queries file
    """
    print('Create all tables')
    for query in create_table_queries:
        print('Executing query: ' + query + ' ')
        cur.execute(query)
        conn.commit()


def main():
    """
    Set up database, drop existing tables, create new tables
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    print('Successfuly connected to the cluster')

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()