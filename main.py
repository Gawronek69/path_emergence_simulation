from model import HelloModel


def main():
    model: HelloModel = HelloModel(12)
    model.step()

if __name__ == '__main__':
    main()