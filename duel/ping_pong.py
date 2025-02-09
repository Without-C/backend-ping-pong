import asyncio


class KeyState:
    """
    어떤 키가 눌려있는지, 아닌지 추적하는 클래스
    """

    def __init__(self):
        self.key_state = {}

    def set_key_state(self, key, state):
        if state == "press":
            self.key_state[key] = True
        elif state == "release":
            self.key_state[key] = False

    def get_key_state(self, key):
        return self.key_state.get(key, False)


class Ball:
    """
    핑퐁의 공을 담당
    """

    def __init__(self, x, y, vx, vy, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def collide_with_rect(self, rect):
        left = rect.x - rect.width / 2
        top = rect.y - rect.height / 2
        right = rect.x + rect.width / 2
        bottom = rect.y + rect.height / 2

        closest_x = max(left, min(self.x, right))
        closest_y = max(top, min(self.y, bottom))

        dx = self.x - closest_x
        dy = self.y - closest_y

        if dx * dx + dy * dy < self.radius * self.radius:
            if abs(dx) > abs(dy):
                self.vx = -self.vx
            else:
                self.vy = -self.vy
            return True
        return False


class Rectangle:
    """
    핑퐁에서 벽과 패들을 담당
    """

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class PingPong:
    def __init__(self, player1, player2, on_update):
        self.on_update = on_update
        self.player1 = player1
        self.player2 = player2

        self.width = 600
        self.height = 400
        self.tick = 0
        self.timedelta = 1 / 60
        self.paddle_speed = 5
        self.paddle_width = 10
        self.paddle_height = 100
        self.wall_depth = 10

        self.ball = Ball(self.width / 2, self.height / 2, 5, 5, 10)
        self.wall_top = Rectangle(
            self.width / 2, -self.wall_depth / 2, self.width, self.wall_depth
        )
        self.wall_bottom = Rectangle(
            self.width / 2,
            self.height + self.wall_depth / 2,
            self.width,
            self.wall_depth,
        )
        self.wall_left = Rectangle(
            -self.wall_depth / 2, self.height / 2, self.wall_depth, self.height
        )
        self.wall_right = Rectangle(
            self.width + self.wall_depth / 2,
            self.height / 2,
            self.wall_depth,
            self.height,
        )
        self.player1_key_state = KeyState()
        self.player2_key_state = KeyState()
        self.paddle1 = Rectangle(
            30, self.height / 2, self.paddle_width, self.paddle_height
        )
        self.paddle2 = Rectangle(
            570, self.height / 2, self.paddle_width, self.paddle_height
        )

    def get_game_state(self):
        return {
            "ball": {
                "x": self.ball.x,
                "y": self.ball.y,
            },
            "paddle1": {
                "x": self.paddle1.x,
                "y": self.paddle1.y,
                "width": self.paddle1.width,
                "height": self.paddle1.height,
            },
            "paddle2": {
                "x": self.paddle2.x,
                "y": self.paddle2.y,
                "width": self.paddle2.width,
                "height": self.paddle2.height,
            },
        }

    async def game_loop(self):
        while True:
            # 게임 상태 업데이트 (패들 움직임, 공 물리 계산 등등)
            self.update()

            # 게임 상태 전송
            await self.on_update(self.get_game_state())

            # 루트 간격 조절
            await asyncio.sleep(self.timedelta)
            self.tick += 1

    def update(self):
        # 패들 움직이기
        for key_state, paddle in [
            (self.player1_key_state, self.paddle1),
            (self.player2_key_state, self.paddle2),
        ]:
            if key_state.get_key_state("ArrowUp") or key_state.get_key_state("w"):
                paddle.y -= self.paddle_speed
            if key_state.get_key_state("ArrowDown") or key_state.get_key_state("s"):
                paddle.y += self.paddle_speed

        # 공 충돌 판정, 방향 바꾸기
        for rect in [
            self.wall_top,
            self.wall_bottom,
            self.wall_left,
            self.wall_right,
            self.paddle1,
            self.paddle2,
        ]:
            self.ball.collide_with_rect(rect)

        # 공 전진
        self.ball.update()

    def on_event(self, participant, event):
        """
        플래이어의 입력을 처리하는 메소드
        """
        action = event["action"]

        # 플레이어가 키를 press/release 했을 때 키 상태 갱신
        if action == "key":
            key = event["key"]
            state = event["state"]

            # 어떤 플레이어가 누른 것인지 구별
            if participant == self.player1:
                self.player1_key_state.set_key_state(key, state)
            elif participant == self.player2:
                self.player2_key_state.set_key_state(key, state)
