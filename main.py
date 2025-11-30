import uvicorn


def main():
    print("Hello from movera!")


if __name__ == "__main__":
    uvicorn.run("backend.backend:app", host="0.0.0.0", port=8888, reload=True)
