import { SessionProvider } from "./app/session-context";
import { AppRouter } from "./routes/app-router";

function App() {
  return (
    <SessionProvider>
      <AppRouter />
    </SessionProvider>
  );
}

export default App;
