import sqlite3


class Sqlite3_db():
    def __init__(self):
        self.connection = sqlite3.connect("sql/sql.db")
        self.cursor = self.connection.cursor()

        # Create blacklisted_channels table
        sql_command = """
        CREATE TABLE IF NOT EXISTS blacklisted_channels (
        channel_id VARCHAR(30) NOT NULL PRIMARY KEY,
        guild_id VARCHAR(30) NOT NULL
        );
        """
        self.cursor.execute(sql_command)

        sql_command = """
        CREATE TABLE IF NOT EXISTS admins (
        user_id VARCHAR(30) NOT NULL,
        guild_id VARCHAR(30) NOT NULL
        );
        """
        self.cursor.execute(sql_command)

        sql_command = """
        DROP TABLE IF EXISTS batch_tags;
        """
        self.cursor.execute(sql_command)

        sql_command = """
        CREATE TABLE IF NOT EXISTS batch_tags (
        guild_id VARCHAR(30) NOT NULL,
        author_id VARCHAR(30) NOT NULL,
        channel_id VARCHAR(30) NOT NULL,
        tag_name VARCHAR(30) NOT NULL
        );
        """
        self.cursor.execute(sql_command)

        sql_command = """
        CREATE UNIQUE INDEX batch_tags_u
        ON batch_tags (guild_id, author_id, channel_id
        );
        """
        self.cursor.execute(sql_command)

        self.connection.commit()
        return

    def add_blacklist_channel(self, guild_id: str, channel_id: str):
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        sql_command = """
        INSERT INTO blacklisted_channels (guild_id, channel_id) VALUES (?, ?);
        """
        try:
            self.cursor.execute(sql_command, (guild_id, channel_id))
            self.connection.commit()
        except Exception as e:
            print(e)
            return

        return

    def set_channel_author_tag(self, guild_id: str, channel_id: str, author_id: str, tag_name: str):
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        author_id = str(author_id)
        tag_name = str(tag_name)
        sql_command = """
        INSERT OR REPLACE INTO batch_tags (guild_id, channel_id, author_id, tag_name)
        VALUES (?, ?, ?,
            COALESCE((SELECT tag_name FROM batch_tags WHERE guild_id = ? AND channel_id = ? AND author_id = ?), ?)
        );
        """

        try:
            self.cursor.execute(sql_command, (guild_id, channel_id, author_id, guild_id, channel_id, author_id, tag_name))
            self.connection.commit()
        except Exception as e:
            print(e)
            return

        return

    def add_admin(self, guild_id: str, user_id: str):
        guild_id = str(guild_id)
        user_id = str(user_id)
        sql_command = """
        INSERT INTO admins (guild_id, user_id) VALUES (?, ?);
        """

        try:
            self.cursor.execute(sql_command, (guild_id, user_id))
            self.connection.commit()
        except Exception as e:
            print(e)
            return

        return

    def remove_admin(self, guild_id: str, user_id: str):
        guild_id = str(guild_id)
        user_id = str(user_id)
        sql_command = """
        DELETE FROM admins WHERE (guild_id=? AND user_id=?);
        """

        try:
            self.cursor.execute(sql_command, (guild_id, user_id))
            self.connection.commit()
        except Exception as e:
            print(e)
            return

        return

    # TODO
    def remove_channel(self, guild_id: str, channel_id: str):
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        sql_command = """
        DELETE FROM blacklisted_channels WHERE (guild_id=? AND channel_id=?);
        """

        try:
            self.cursor.execute(sql_command, (guild_id, channel_id))
            self.connection.commit()
        except Exception as e:
            print(e)
            return

        return

    def get_blacklisted_channels(self, guild_id: str):
        guild_id = str(guild_id)
        sql_command = """
        SELECT channel_id FROM blacklisted_channels WHERE guild_id = ?;
        """
        self.cursor.execute(sql_command, (guild_id,))

        result_tuples = self.cursor.fetchall()
        print(result_tuples)

        result = [t[0] for t in result_tuples]
        print(result)

        return result

    def get_admins(self, guild_id: str):
        guild_id = str(guild_id)
        sql_command = """
        SELECT user_id FROM admins WHERE guild_id = ?;
        """
        self.cursor.execute(sql_command, (guild_id,))

        result_tuples = self.cursor.fetchall()
        print(result_tuples)

        result = [t[0] for t in result_tuples]
        print(result)

        return result

    def get_btag(self, guild_id: str, channel_id: str, author_id: str):
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        author_id = str(author_id)

        sql_command = """
        SELECT tag_name FROM batch_tags WHERE guild_id = ? AND channel_id = ? AND author_id = ?;
        """
        self.cursor.execute(sql_command, (guild_id,channel_id,author_id))

        result_tuples = self.cursor.fetchall()
        print(result_tuples)

        result = [t[0] for t in result_tuples]
        try:
            result = result[0]
        except IndexError:
            result = ''
        print(result)

        return result
