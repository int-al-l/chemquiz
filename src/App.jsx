import { Route, Routes } from "react-router-dom";

import MainPage from "./pages/MainPage";
import ExplorePage from "./pages/ExplorePage";
import DeckPage from "./pages/DeckPage";
import MyListPage from "./pages/MyListPage";
import QuizSetupPage from "./pages/QuizSetupPage";
import QuizPage from "./pages/QuizPage";
import QuizResultsPage from "./pages/QuizResultsPage";
import NotFoundPage from "./pages/NotFoundPage";
import SignInPage from "./pages/SignInPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import ProfilePage from "./pages/ProfilePage";
import LiveSetupPage from "./live/LiveSetupPage";
import LiveHostPage from "./live/LiveHostPage";
import JoinPage from "./live/JoinPage";
import LivePlayPage from "./live/LivePlayPage";
import LiveHistoryPage from "./live/LiveHistoryPage";
import LiveGamePage from "./live/LiveGamePage";
import MyQuizzesPage from "./quizzes/MyQuizzesPage";
import QuizEditorPage from "./quizzes/QuizEditorPage";
import Toaster from "./components/Toaster";
import AppShell from "./components/AppShell";

import { AuthProvider } from "./auth/AuthProvider";
import { LanguageProvider } from "./i18n/LanguageProvider";
import { ProgressProvider } from "./progress/ProgressProvider";
import { SavedProvider } from "./saved/SavedProvider";

import "./App.css";
import "./learn.css";
import "./live/live.css";
import "./quizzes/quizzes.css";
import "./theme/odan.css";
import "./pages/MainPage.css";

/**
 * Every screen has a URL, so the browser's back button, a refresh mid-quiz and
 * a shared link all behave the way people expect.
 *
 *   /                        menu, level and streak
 *   /explore                 every deck, with progress
 *   /explore/:slug           one deck as flashcards (?mode=study|grid)
 *   /explore/all             every card;  /explore/saved  My list as a deck
 *   /review                  cards due for spaced review
 *   /list                    saved items
 *   /profile                 level, badges, daily goal, account
 *   /sign-in                 sign in or create an account
 *   /verify-email            the emailed code (or ?token= from the link)
 *   /reset-password          forgotten password
 *   /quiz/setup[/:slug]      choose mode and length
 *   /quiz/:token             a quiz in progress
 *   /quiz/:token/results     the score afterwards
 *   /live                    set up a class game (the board)
 *   /live/host/:pin          the board during a class game
 *   /live/history            a signed-in teacher's past class games
 *   /live/history/:id        one past game: standings, CSV, play again
 *   /join[/:pin]             a student joins with the PIN (the QR code fills it in)
 *   /play/:pin               a student's phone during the game
 *   /quizzes                 a teacher's own quizzes
 *   /quizzes/new, /:id       the quiz editor
 *   /quizzes/:id/play        play your own quiz alone
 */
function App() {
  return (
    <LanguageProvider>
    <AuthProvider>
      <SavedProvider>
        <ProgressProvider>
          <Routes>
            {/* Places: inside the sidebar / tab-bar frame. */}
            <Route element={<AppShell />}>
              <Route path="/" element={<MainPage />} />

              <Route path="/explore" element={<ExplorePage />} />
              <Route path="/list" element={<MyListPage />} />
              <Route path="/profile" element={<ProfilePage />} />

              <Route path="/quiz/setup" element={<QuizSetupPage />} />
              <Route path="/quiz/setup/:slug" element={<QuizSetupPage />} />
              <Route path="/quiz/:token/results" element={<QuizResultsPage />} />

              <Route path="/live" element={<LiveSetupPage />} />
              <Route path="/live/history" element={<LiveHistoryPage />} />
              <Route path="/live/history/:id" element={<LiveGamePage />} />
              <Route path="/quizzes" element={<MyQuizzesPage />} />
              <Route path="/quizzes/new" element={<QuizEditorPage />} />
              <Route path="/quizzes/:id" element={<QuizEditorPage />} />
              <Route path="/join" element={<JoinPage />} />
              <Route path="/join/:pin" element={<JoinPage />} />

              <Route path="/sign-in" element={<SignInPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

              <Route path="*" element={<NotFoundPage />} />
            </Route>

            {/* Focused screens: the whole window. */}
            <Route path="/explore/:slug" element={<DeckPage />} />
            <Route path="/review" element={<DeckPage review />} />
            <Route path="/quiz/:token" element={<QuizPage />} />
            <Route path="/live/host/:pin" element={<LiveHostPage />} />
            <Route path="/play/:pin" element={<LivePlayPage />} />
          </Routes>
          <Toaster />
        </ProgressProvider>
      </SavedProvider>
    </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
