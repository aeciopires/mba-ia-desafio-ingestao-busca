from src.search import search_prompt


def main() -> None:
    print("Chat de busca semântica iniciado. Digite 'sair' para encerrar.")

    while True:
        try:
            question = input("\nPERGUNTA: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o chat.")
            break

        if not question:
            continue

        if question.lower() in {"sair", "exit", "quit"}:
            print("Encerrando o chat.")
            break

        try:
            answer = search_prompt(question)
            print("\nRESPOSTA:", answer)
        except Exception as error:
            print(f"Erro durante a consulta: {error}")
            break


if __name__ == "__main__":
    main()