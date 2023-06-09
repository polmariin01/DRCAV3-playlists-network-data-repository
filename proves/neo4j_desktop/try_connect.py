import logging

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

#CREATE CONSTRAINS
    def create_constraints(self):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.execute_write(
                self._create_constraints)
            print("Created constraints")

    @staticmethod
    def _create_constraints(tx):
        # Envia una Query a la base de dades i després retorna només un string amb el nom
        query = (
            "CREATE CONSTRAINT FOR (p:Playlist) REQUIRE p.name IS UNIQUE "
            "CREATE CONSTRAINT FOR (s:Song) REQUIRE s.title IS UNIQUE"
        )
        tx.run(query)


#CREATE PLAYLIST
    def create_playlist(self, playlist_name):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.execute_write(
                self._create_and_return_playlist, playlist_name)
            for record in result:
                print("Created playlist: {p}".format(p=record['p']))

    @staticmethod
    def _create_and_return_playlist(tx, playlist_name : str, properties : dict = {}):
        # Envia una Query a la base de dades i després retorna només un string amb el nom
        query = (
            "CREATE (p:Playlist { name : $playlist_name})"
            "RETURN p"
        )
        result = tx.run(query, playlist_name=playlist_name)
        #print(result)
        try:
            return [{"p": record["p"]["name"]}
                    for record in result]
            return result #de moment no s'accedeix, es pot fer per a tornar el diccionari sencer 
            return [{"p": record["p"]}
                    for record in result] # De moment tampoc s'accedeix, podem possarho per tornar l'objecte p sencer
        # Capture any errors along with the query and data for traceability
        except Neo4jError as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

#CREATE SONG
    def create_song(self, song_title):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.execute_write(
                self._create_and_return_song, song_title)
            for record in result:
                print("Created song: {s}".format(s=record['s']))

    @staticmethod
    def _create_and_return_song(tx, song_title : str, properties : dict = {}):
        # Envia una Query a la base de dades i després retorna només un string amb el nom
        query = (
            "CREATE (s:Song { title : $song_title})"
            "RETURN s"
        )
        result = tx.run(query, song_title=song_title)
        #print(result)
        try:
            return [{"s": record["s"]["title"]} for record in result]
        # Capture any errors along with the query and data for traceability
        except Neo4jError as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

#FICAR CANÇONS NOVES A PLAYLISTS
    @staticmethod
    def _create_and_return_track_in_playlist(tx, song_name, playlist_name):
        query = (
            "CREATE (s:Song { title: $song_name})"          #CREA UNA CANÇÓ
            "MATCH (p:Playlist { name: $playlist_name})"    #BUSCA UNA PLAYLIST EXISTENT
            "CREATE (p)-[:CONTAINS]->(s)"                   #CREA UNA RELACIÓ AMB LA PLAYLIST I LA CANÇÓ
            "RETURN p, s"                                   #RETORNA ELS DOS OBJECTES
        ) 



    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        try:
            return [{"p1": record["p1"]["name"], "p2": record["p2"]["name"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except Neo4jError as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_person, person_name)
            for record in result:
                print("Found person: {record}".format(record=record))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [record["name"] for record in result]


if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "DRCAV1234"
    app = App(uri, user, password)
    app.create_constraints()
    app.create_playlist("Musica para estudiar")
    app.create_song("Titi me preguntó")
#    app.create_friendship("Alice", "David")
#    app.find_person("Alice")
    app.close()