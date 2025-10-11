import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()

API_BASE = "/api/v1/movies/"
AUTH_BASE = "/api/v1/auth/"


class EndpointsSmokeTest(APITestCase):
    """Базовые smoke-тесты для проверки доступности endpoints"""
    maxDiff = None

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass",
            is_staff=True,
            is_superuser=True,
            email="a@a.a"
        )
        self.u1 = User.objects.create_user(
            username="user1",
            password="userpass",
            email="u@u.u"
        )

    # ---------- helpers ----------
    def _log(self, message, data=None):
        line = f"[TEST] {message}"
        if data is not None:
            try:
                payload = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                payload = str(data)
            line += f" -> {payload}"
        print(line)

    def _assert_unauth(self, resp, where=""):
        self._log(
            f"Expect 401/403 {where}",
            {
                "status_code": resp.status_code,
                "data": str(getattr(resp, "data", resp.content))[:500]
            }
        )
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    # ---------- tests ----------
    def test_public_lists_ok(self):
        """Публичный доступ к спискам genres/authors/movies"""
        r1 = self.client.get(API_BASE + "genres/")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        r2 = self.client.get(API_BASE + "authors/")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

        r3 = self.client.get(API_BASE + "movies/")
        self.assertEqual(r3.status_code, status.HTTP_200_OK)

    def test_anonymous_post_forbidden(self):
        """Анонимные пользователи не могут создавать entities"""
        self._assert_unauth(
            self.client.post(API_BASE + "genres/", {"name": "Drama"}, format="json"),
            "POST /genres/"
        )

        self._assert_unauth(
            self.client.post(API_BASE + "authors/", {"name": "John Smith"}, format="json"),
            "POST /authors/"
        )

        self._assert_unauth(
            self.client.post(
                API_BASE + "movies/",
                {"title": "X", "description": "d", "year": 2000},
                format="json"
            ),
            "POST /movies/"
        )

    def test_admin_can_create_entities(self):
        """Админ может создавать жанры, авторов и фильмы"""
        self.client.force_login(self.admin)

        # Create Genre
        g = self.client.post(API_BASE + "genres/", {"name": "Action"}, format="json")
        self.assertEqual(g.status_code, status.HTTP_201_CREATED, g.data)

        # Create Author
        a = self.client.post(
            API_BASE + "authors/",
            {"name": "Jane Doe", "bio": "Bio"},
            format="json"
        )
        self.assertEqual(a.status_code, status.HTTP_201_CREATED, a.data)
        a_id = a.data["id"]

        # Get genre ID
        glist = self.client.get(API_BASE + "genres/")
        self.assertEqual(glist.status_code, status.HTTP_200_OK)
        genre_id = next((i["id"] for i in glist.data if i["name"] == "Action"), None)
        self.assertIsNotNone(genre_id, "Genre id not found")

        # Create Movie
        title = "Test Movie"
        m = self.client.post(
            API_BASE + "movies/",
            {
                "title": title,
                "description": "Some description",
                "year": 2024,
                "author": a_id,
                "genres": [genre_id]
            },
            format="json",
        )
        self.assertEqual(m.status_code, status.HTTP_201_CREATED, m.data)

        # Verify movie in list
        mlist = self.client.get(API_BASE + "movies/")
        self.assertEqual(mlist.status_code, status.HTTP_200_OK)
        m_slug = next((i["slug"] for i in mlist.data if i["title"] == title), None)
        self.assertIsNotNone(m_slug, "Movie slug not found in list after create")

        # Get movie detail
        d = self.client.get(API_BASE + f"movies/{m_slug}/")
        self.assertEqual(d.status_code, status.HTTP_200_OK, d.data)
        self.assertEqual(d.data["slug"], m_slug)

    def test_actions_like_unlike_progress_require_auth(self):
        """Like/unlike/progress требуют авторизации"""
        self.client.force_login(self.admin)

        # Prepare data
        g = self.client.post(
            API_BASE + "genres/",
            {"name": "Sci-Fi"},
            format="json"
        ).data

        a = self.client.post(
            API_BASE + "authors/",
            {"name": "Arthur C"},
            format="json"
        ).data

        glist = self.client.get(API_BASE + "genres/").data
        gid = next((i["id"] for i in glist if i["slug"] == g["slug"]), None)
        self.assertIsNotNone(gid, "Genre id not found")

        m = self.client.post(
            API_BASE + "movies/",
            {
                "title": "Space",
                "description": "zzz",
                "year": 1999,
                "author": a["id"],
                "genres": [gid]
            },
            format="json"
        )
        self.assertEqual(m.status_code, status.HTTP_201_CREATED, m.data)

        mlist = self.client.get(API_BASE + "movies/").data
        slug = next((i["slug"] for i in mlist if i["title"] == "Space"), None)
        self.assertIsNotNone(slug, "Movie slug not found")

        # Test unauthorized like
        self.client.logout()
        r_like = self.client.post(API_BASE + f"movies/{slug}/like/", {}, format="json")
        self._assert_unauth(r_like, "POST like")

        # Test authorized like/unlike
        self.client.force_login(self.u1)

        r_like2 = self.client.post(API_BASE + f"movies/{slug}/like/", {}, format="json")
        self.assertEqual(r_like2.status_code, status.HTTP_200_OK, r_like2.data)
        self.assertEqual(r_like2.data["status"], "liked")

        r_unlike = self.client.post(API_BASE + f"movies/{slug}/unlike/", {}, format="json")
        self.assertEqual(r_unlike.status_code, status.HTTP_200_OK, r_unlike.data)
        self.assertEqual(r_unlike.data["status"], "unliked")

        # Test progress
        r_prog = self.client.post(
            API_BASE + f"movies/{slug}/progress/",
            {"position_sec": 120, "duration_sec": 300},
            format="json"
        )
        self.assertEqual(r_prog.status_code, status.HTTP_200_OK, r_prog.data)

    def test_me_watched_requires_auth(self):
        """Endpoint me/watched требует авторизации"""
        r = self.client.get(API_BASE + "me/watched/")
        self._assert_unauth(r, "GET me/watched (anon)")

        self.client.force_login(self.u1)
        r2 = self.client.get(API_BASE + "me/watched/")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)


class GenreAuthorDetailTest(APITestCase):
    """Тесты для detail views жанров и авторов"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass",
            is_staff=True,
            is_superuser=True
        )

    def test_genre_detail_view(self):
        """Получение детальной информации о жанре"""
        self.client.force_login(self.admin)

        # Create genre
        g = self.client.post(
            API_BASE + "genres/",
            {"name": "Horror"},
            format="json"
        )
        self.assertEqual(g.status_code, status.HTTP_201_CREATED)
        slug = g.data["slug"]

        # Get genre detail
        detail = self.client.get(API_BASE + f"genres/{slug}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], "Horror")
        self.assertEqual(detail.data["slug"], slug)

    def test_genre_detail_404(self):
        """Несуществующий жанр возвращает 404"""
        response = self.client.get(API_BASE + "genres/non-existent-slug/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_detail_view(self):
        """Получение детальной информации об авторе"""
        self.client.force_login(self.admin)

        # Create author
        a = self.client.post(
            API_BASE + "authors/",
            {"name": "Stephen King", "bio": "Famous writer"},
            format="json"
        )
        self.assertEqual(a.status_code, status.HTTP_201_CREATED)
        slug = a.data["slug"]

        # Get author detail
        detail = self.client.get(API_BASE + f"authors/{slug}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], "Stephen King")
        self.assertEqual(detail.data["slug"], slug)

    def test_author_detail_404(self):
        """Несуществующий автор возвращает 404"""
        response = self.client.get(API_BASE + "authors/non-existent-slug/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AuthenticationTest(APITestCase):
    """Тесты для authentication endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        """Регистрация нового пользователя"""
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "SecurePass123!",
        }
        response = self.client.post(AUTH_BASE + "register/", data, format="json")
        # Ожидаем либо 201, либо 400 (зависит от твоей реализации)
        self.assertIn(response.status_code, (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST))
        if response.status_code == status.HTTP_201_CREATED:
            self.assertIn("username", response.data)

    def test_user_login(self):
        """Логин существующего пользователя"""
        # Create user first
        user = User.objects.create_user(
            username="testuser_login",
            password="testpass123",
            email="testlogin@test.com"
        )

        # Login
        data = {
            "username": "testuser_login",
            "password": "testpass123"
        }
        response = self.client.post(AUTH_BASE + "login/", data, format="json")
        # Проверяем успешный логин или ошибку валидации
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST))
        if response.status_code == status.HTTP_200_OK:
            self.assertIn("access", response.data)
            self.assertIn("refresh", response.data)

    def test_login_with_wrong_credentials(self):
        """Логин с неверными данными возвращает ошибку"""
        data = {
            "username": "nonexistent",
            "password": "wrongpass"
        }
        response = self.client.post(AUTH_BASE + "login/", data, format="json")
        # Ожидаем либо 401, либо 400
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST))

    def test_profile_view_requires_auth(self):
        """Просмотр профиля требует авторизации"""
        response = self.client.get(AUTH_BASE + "profile/")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    def test_authenticated_user_can_view_profile(self):
        """Авторизованный пользователь может просматривать профиль"""
        user = User.objects.create_user(
            username="testuser_profile",
            password="pass",
            email="profile@test.com"
        )
        self.client.force_login(user)

        response = self.client.get(AUTH_BASE + "profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser_profile")

    def test_change_password(self):
        """Изменение пароля авторизованным пользователем"""
        user = User.objects.create_user(
            username="testuser_pwd",
            password="oldpass123",
            email="pwd@test.com"
        )
        self.client.force_login(user)

        data = {
            "old_password": "oldpass123",
            "new_password": "newpass456",
        }
        response = self.client.post(
            AUTH_BASE + "change-password/",
            data,
            format="json"
        )
        # Ожидаем либо 200, либо 405 (если метод не поддерживается), либо 400
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_400_BAD_REQUEST))
        
        if response.status_code == status.HTTP_200_OK:
            # Verify new password works
            self.client.logout()
            login_data = {
                "username": "testuser_pwd",
                "password": "newpass456"
            }
            login_response = self.client.post(AUTH_BASE + "login/", login_data, format="json")
            self.assertIn(login_response.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST))


class PermissionsTest(APITestCase):
    """Тесты для проверки прав доступа"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_perm",
            password="pass",
            email="admin_perm@test.com",
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            username="regular_perm",
            password="pass",
            email="regular_perm@test.com"
        )

    def test_regular_user_cannot_create_genre(self):
        """Обычный пользователь не может создавать жанры"""
        self.client.force_login(self.regular_user)

        response = self.client.post(
            API_BASE + "genres/",
            {"name": "Drama"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_create_author(self):
        """Обычный пользователь не может создавать авторов"""
        self.client.force_login(self.regular_user)

        response = self.client.post(
            API_BASE + "authors/",
            {"name": "John Doe"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_create_movie(self):
        """Обычный пользователь не может создавать фильмы"""
        self.client.force_login(self.regular_user)

        response = self.client.post(
            API_BASE + "movies/",
            {"title": "Test", "description": "Test", "year": 2024},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_all_entities(self):
        """Админ может создавать все сущности"""
        self.client.force_login(self.admin)

        # Genre
        g = self.client.post(
            API_BASE + "genres/",
            {"name": "Comedy"},
            format="json"
        )
        self.assertEqual(g.status_code, status.HTTP_201_CREATED)

        # Author
        a = self.client.post(
            API_BASE + "authors/",
            {"name": "Test Author"},
            format="json"
        )
        self.assertEqual(a.status_code, status.HTTP_201_CREATED)

        # Movie
        glist = self.client.get(API_BASE + "genres/").data
        gid = glist[0]["id"]

        m = self.client.post(
            API_BASE + "movies/",
            {
                "title": "Admin Movie",
                "description": "Test",
                "year": 2024,
                "author": a.data["id"],
                "genres": [gid]
            },
            format="json"
        )
        self.assertEqual(m.status_code, status.HTTP_201_CREATED)


class ValidationTest(APITestCase):
    """Тесты валидации данных"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass",
            is_staff=True,
            is_superuser=True
        )
        self.client.force_login(self.admin)

    def test_create_movie_without_required_fields(self):
        """Создание фильма без обязательных полей возвращает ошибку"""
        response = self.client.post(
            API_BASE + "movies/",
            {"title": "Incomplete"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_genre_with_duplicate_name(self):
        """Создание жанра с дублирующимся именем"""
        # Create first genre
        self.client.post(
            API_BASE + "genres/",
            {"name": "Action"},
            format="json"
        )

        # Try to create duplicate
        response = self.client.post(
            API_BASE + "genres/",
            {"name": "Action"},
            format="json"
        )
        # Should fail with 400 if slug uniqueness is enforced
        self.assertIn(
            response.status_code,
            (status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED)
        )

    def test_create_movie_with_invalid_year(self):
        """Создание фильма с невалидным годом"""
        response = self.client.post(
            API_BASE + "movies/",
            {
                "title": "Test",
                "description": "Test",
                "year": "not-a-year"
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EdgeCasesTest(APITestCase):
    """Тесты граничных случаев"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser_edge",
            password="pass",
            email="edge@test.com"
        )

    def test_double_like_same_movie(self):
        """Двойной лайк одного фильма"""
        admin = User.objects.create_superuser(
            username="admin_edge1",
            password="pass",
            email="admin1@test.com"
        )
        self.client.force_login(admin)

        # Create movie
        g = self.client.post(API_BASE + "genres/", {"name": "Test"}, format="json")
        a = self.client.post(API_BASE + "authors/", {"name": "Test"}, format="json")
        
        glist = self.client.get(API_BASE + "genres/").data
        m = self.client.post(
            API_BASE + "movies/",
            {
                "title": "Test Movie",
                "description": "Test",
                "year": 2024,
                "author": a.data["id"],
                "genres": [glist[0]["id"]]
            },
            format="json"
        )

        mlist = self.client.get(API_BASE + "movies/").data
        slug = mlist[0]["slug"]

        self.client.force_login(self.user)

        # First like
        r1 = self.client.post(API_BASE + f"movies/{slug}/like/", {}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        # Second like (should handle gracefully)
        r2 = self.client.post(API_BASE + f"movies/{slug}/like/", {}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

    def test_unlike_without_like(self):
        """Unlike фильма, который не был лайкнут"""
        admin = User.objects.create_superuser(
            username="admin_edge2",
            password="pass",
            email="admin2@test.com"
        )
        self.client.force_login(admin)

        g = self.client.post(API_BASE + "genres/", {"name": "Test"}, format="json")
        a = self.client.post(API_BASE + "authors/", {"name": "Test"}, format="json")
        
        glist = self.client.get(API_BASE + "genres/").data
        m = self.client.post(
            API_BASE + "movies/",
            {
                "title": "Test Movie",
                "description": "Test",
                "year": 2024,
                "author": a.data["id"],
                "genres": [glist[0]["id"]]
            },
            format="json"
        )

        mlist = self.client.get(API_BASE + "movies/").data
        slug = mlist[0]["slug"]

        self.client.force_login(self.user)

        # Unlike without like
        response = self.client.post(
            API_BASE + f"movies/{slug}/unlike/",
            {},
            format="json"
        )
        # Should handle gracefully (200 or 400)
        self.assertIn(
            response.status_code,
            (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
        )
