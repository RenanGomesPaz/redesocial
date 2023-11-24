from neo4j import GraphDatabase

class RedeSocial:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def add_person(self, nome, idade, local):
        with self._driver.session() as session:
            session.write_transaction(self._create_person, nome, idade, local)

    def _create_person(self, tx, nome, idade, local):
        tx.run("CREATE (p:Person {nome: $nome, idade: $idade, local: $local})", nome=nome, idade=idade, local=local)

    def display_people(self):
        with self._driver.session() as session:
            result = session.read_transaction(self._get_people)
            for record in result:
                print(f"ID: {record['id']}, nome: {record['nome']}")

    def _get_people(self, tx):
        result = tx.run("MATCH (p:Person) RETURN ID(p) AS id, p.nome AS nome")
        return result

    def add_friendship(self, person1_id, person2_id):
        with self._driver.session() as session:
            session.write_transaction(self._create_friendship, person1_id, person2_id)

    def _create_friendship(self, tx, person1_id, person2_id):
        tx.run("MATCH (p1:Person), (p2:Person) WHERE ID(p1) = $person1_id AND ID(p2) = $person2_id "
               "CREATE (p1)-[:FRIEND_OF]->(p2)", person1_id=person1_id, person2_id=person2_id)

    def display_friendship_network(self, person_id):
        with self._driver.session() as session:
            result = session.read_transaction(self._get_friendship_network, person_id)
            for record in result:
                print(f"Rede de Amizades de {record['nome']}: {record['amigos']}")

    def _get_friendship_network(self, tx, person_id):
        result = tx.run("MATCH (p:Person)-[:FRIEND_OF*]-(friend) WHERE ID(p) = $person_id "
                        "RETURN p.nome AS nome, COLLECT(friend.nome) AS amigos", person_id=person_id)
        return result

    def remove_person(self, person_id):
        with self._driver.session() as session:
            session.write_transaction(self._delete_person, person_id)

    def _delete_person(self, tx, person_id):
        tx.run("MATCH (p:Person) WHERE ID(p) = $person_id DETACH DELETE p", person_id=person_id)

neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "12345"

social_network = RedeSocial(neo4j_uri, neo4j_user, neo4j_password)

# Exemplo:
social_network.add_person("Maria", 25, "Nova York")
social_network.add_person("João", 30, "São Francisco")

social_network.display_people()

social_network.add_friendship(1, 2)

social_network.display_friendship_network(1)

social_network.remove_person(1)

social_network.close()
