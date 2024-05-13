public class Server {
    public Server() {
    }

    public void start() {
        HandlerTask handlerTask = new HandlerTask(12_345);
        handlerTask.run();
    }
}
