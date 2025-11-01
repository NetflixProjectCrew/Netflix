import { BrowserRouter, Routes, Route, useNavigate, useSearchParams } from "react-router-dom";
import AuthProvider from "./context/AuthContext";
import SubscriptionProvider from "./context/SubscriptionContext";
import { GuestOnlyRoute, RequireAuth, RequireSubscription } from "./router/guards";

import Header from "./components/common/Header";
import WelcomePage from "./pages/WelcomePage";
import AuthPage from "./pages/AuthPage";            // login/register switch
import SubscribePage from "./pages/SubscribePage";  // выбор плана и checkout
import BrowsePage from "./pages/BrowsePage";        // rows с фильмами
import WatchPage from "./pages/WatchPage";          // плеер
import MovieModal from "./components/modals/MovieModal";

function BrowseWithModal() {
  const [params, setParams] = useSearchParams();
  const slug = params.get("modal");
  const nav = useNavigate();
  const close = () => { params.delete("modal"); setParams(params, { replace:true }); };

  return (
    <>
      <BrowsePage onMovieClick={(slug) => setParams({ modal: slug })} />
      {slug && <MovieModal slug={slug} onClose={close} onPlay={() => nav(`/watch/${slug}`)} />}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <SubscriptionProvider>
        <BrowserRouter>
          <Header/> {/* рендерит разные кнопки по useAuth/useSubscription */}
          <Routes>
            <Route element={<GuestOnlyRoute/>}>
              <Route path="/" element={<WelcomePage/>} />
              <Route path="/welcome" element={<WelcomePage/>} />
              <Route path="/auth" element={<AuthPage/>} />
            </Route>

            <Route element={<RequireAuth/>}>
              <Route path="/subscribe" element={<SubscribePage/>} />
            </Route>

            <Route element={<RequireSubscription/>}>
              <Route path="/browse" element={<BrowseWithModal/>} />
              <Route path="/watch/:slug" element={<WatchPage/>} />
            </Route>

            <Route path="*" element={<WelcomePage/>} />
          </Routes>
        </BrowserRouter>
      </SubscriptionProvider>
    </AuthProvider>
  );
}
