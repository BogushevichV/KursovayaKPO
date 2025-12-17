import subprocess
import time


class DockerManager:
    """Класс для управления Docker и контейнерами"""

    def __init__(self, container_name='exam_pg'):
        self.container_name = container_name
        self.docker_started = False
        self.container_started = False

    def start_docker(self):
        """Запуск Docker приложения"""
        try:
            print("Запуск Docker...")
            # Проверяем, запущен ли Docker
            try:
                subprocess.run(
                    ['docker', 'version'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                print("✓ Docker уже запущен")
                self.docker_started = True
                return True
            except:
                # Если docker не запущен, пытаемся запустить Docker Desktop (Windows)
                try:
                    subprocess.Popen(['C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'])
                    print("Ожидание запуска Docker Desktop...")
                    time.sleep(10)
                    print("✓ Docker запущен")
                    self.docker_started = True
                    return True
                except FileNotFoundError:
                    print("❌ Docker Desktop не найден. Убедитесь, что Docker установлен.")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при запуске Docker: {e}")
            return False

    def start_container(self):
        """Запуск существующего контейнера"""
        try:
            print(f"Запуск контейнера {self.container_name}...")
            result = subprocess.run(
                ['docker', 'start', self.container_name],
                capture_output=True,
                text=True,
                check=True
            )
            time.sleep(3)  # Ожидание инициализации PostgreSQL
            print(f"✓ Контейнер {self.container_name} запущен")
            self.container_started = True
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при запуске контейнера: {e}")
            if e.stderr:
                print(f"   Подробности: {e.stderr}")
            return False

    def stop_container(self):
        """Остановка контейнера"""
        if not self.container_started:
            return

        try:
            print(f"\nОстановка контейнера {self.container_name}...")
            subprocess.run(
                ['docker', 'stop', self.container_name],
                capture_output=True,
                check=True
            )
            print(f"✓ Контейнер {self.container_name} остановлен")
            self.container_started = False
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при остановке контейнера: {e}")

    def is_container_running(self):
        """Проверка, запущен ли контейнер"""
        try:
            result = subprocess.run(
                ['docker', 'inspect', '-f', '{{.State.Running}}', self.container_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() == 'true'
        except subprocess.CalledProcessError:
            return False

    def initialize(self):
        print("=" * 80)
        print("ЗАПУСК DOCKER И КОНТЕЙНЕРА")
        print("=" * 80)

        # Запускаем Docker
        if not self.start_docker():
            return False

        # Проверяем, не запущен ли уже контейнер
        if self.is_container_running():
            print(f"✓ Контейнер {self.container_name} уже запущен")
            self.container_started = True
            return True

        # Запускаем контейнер
        if not self.start_container():
            return False

        print("\n" + "=" * 80)
        print("DOCKER И КОНТЕЙНЕР УСПЕШНО ЗАПУЩЕНЫ")
        print("=" * 80 + "\n")

        return True

    def cleanup(self):
        """Очистка: остановка контейнера"""
        self.stop_container()