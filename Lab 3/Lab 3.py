import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

width = 1280
height = 800

class App:
    def __init__(self):
        # initialise pygame
        pg.init()
        pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)
        pg.mouse.set_pos((width/2, height/2))
        pg.mouse.set_visible(False)
        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0
        # initialise opengl
        glClearColor(0.1, 0.1, 0.1, 1)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        self.shaderBasic = self.createShader("shaders/simple_3d_vertex.txt", "shaders/simple_3d_fragment.txt")
        glUseProgram(self.shader)
        self.resetLights()

        projection_transform = pyrr.matrix44.create_perspective_projection(45, width / height, 0.1, 10, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection_transform)

        glUniform3fv(glGetUniformLocation(self.shader, "ambient"), 1, np.array([0.1, 0.1, 0.1], dtype=np.float32))

        glUniform1i(glGetUniformLocation(self.shader, "material.diffuse"), 0)
        glUniform1i(glGetUniformLocation(self.shader, "material.specular"), 1)

        glUseProgram(self.shaderBasic)

        glUniformMatrix4fv(glGetUniformLocation(self.shaderBasic, "projection"), 1, GL_FALSE, projection_transform)

        glEnable(GL_DEPTH_TEST)

        self.wood_texture = Material("gfx/crate")
        self.cube = Cube(self.shader, self.wood_texture, [1, 1, 0.5])
        self.player = Player([0, 0, 1.2])
        self.light = Light([self.shaderBasic, self.shader], [0.2, 0.7, 0.8], [1, 1.7, 1.5], 2, self.lightCount)
        self.lightCount += 1
        self.light2 = Light([self.shaderBasic, self.shader], [0.9, 0.4, 0.0], [0, 1.7, 0.5], 2, self.lightCount)
        self.lightCount += 1
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def resetLights(self):
        glUseProgram(self.shader)
        for i in range(8):
            glUniform1i(glGetUniformLocation(self.shader, f"lights[{i}].enabled"), 0)

    def mainLoop(self):
        running = True
        while (running):
            # check events
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    running = False
            self.handleMouse()
            self.handleKeys()
            # update objects
            self.cube.update()
            self.light.update()
            self.light2.update()
            self.player.update([self.shaderBasic, self.shader])
            # refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.cube.draw()
            self.light.draw()
            self.light2.draw()
            pg.display.flip()

            # timing
            self.showFrameRate()
        self.quit()

    def handleKeys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.player.move(0, 0.0025 * self.frameTime)
            return
        if keys[pg.K_a]:
            self.player.move(90, 0.0025 * self.frameTime)
            return
        if keys[pg.K_s]:
            self.player.move(180, 0.0025 * self.frameTime)
            return
        if keys[pg.K_d]:
            self.player.move(-90, 0.0025 * self.frameTime)
            return

    def handleMouse(self):
        (x, y) = pg.mouse.get_pos()
        theta_increment = self.frameTime * 0.05 * (width/2 - x)
        phi_increment = self.frameTime * 0.05 * (height/2 - y)
        self.player.increment_direction(theta_increment, phi_increment)
        pg.mouse.set_pos((width/2, height/2))

    def showFrameRate(self):
        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = int(1000.0 * self.numFrames / delta)
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / framerate)
        self.numFrames += 1

    def quit(self):
        self.cube.destroy()
        self.wood_texture.destroy()
        self.light.destroy()
        self.light2.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class Cube:
    def __init__(self, shader, material, position):
        self.material = material
        self.shader = shader
        self.position = position
        glUseProgram(shader)
        # x, y, z, s, t, nx, ny, nz
        self.vertices = (
            -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,
            0.5, -0.5, -0.5, 1, 0, 0, 0, -1,
            0.5, 0.5, -0.5, 1, 1, 0, 0, -1,

            0.5, 0.5, -0.5, 1, 1, 0, 0, -1,
            -0.5, 0.5, -0.5, 0, 1, 0, 0, -1,
            -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,

            -0.5, -0.5, 0.5, 0, 0, 0, 0, 1,
            0.5, -0.5, 0.5, 1, 0, 0, 0, 1,
            0.5, 0.5, 0.5, 1, 1, 0, 0, 1,

            0.5, 0.5, 0.5, 1, 1, 0, 0, 1,
            -0.5, 0.5, 0.5, 0, 1, 0, 0, 1,
            -0.5, -0.5, 0.5, 0, 0, 0, 0, 1,

            -0.5, 0.5, 0.5, 1, 0, -1, 0, 0,
            -0.5, 0.5, -0.5, 1, 1, -1, 0, 0,
            -0.5, -0.5, -0.5, 0, 1, -1, 0, 0,

            -0.5, -0.5, -0.5, 0, 1, -1, 0, 0,
            -0.5, -0.5, 0.5, 0, 0, -1, 0, 0,
            -0.5, 0.5, 0.5, 1, 0, -1, 0, 0,

            0.5, 0.5, 0.5, 1, 0, 1, 0, 0,
            0.5, 0.5, -0.5, 1, 1, 1, 0, 0,
            0.5, -0.5, -0.5, 0, 1, 1, 0, 0,

            0.5, -0.5, -0.5, 0, 1, 1, 0, 0,
            0.5, -0.5, 0.5, 0, 0, 1, 0, 0,
            0.5, 0.5, 0.5, 1, 0, 1, 0, 0,

            -0.5, -0.5, -0.5, 0, 1, 0, -1, 0,
            0.5, -0.5, -0.5, 1, 1, 0, -1, 0,
            0.5, -0.5, 0.5, 1, 0, 0, -1, 0,

            0.5, -0.5, 0.5, 1, 0, 0, -1, 0,
            -0.5, -0.5, 0.5, 0, 0, 0, -1, 0,
            -0.5, -0.5, -0.5, 0, 1, 0, -1, 0,

            -0.5, 0.5, -0.5, 0, 1, 0, 1, 0,
            0.5, 0.5, -0.5, 1, 1, 0, 1, 0,
            0.5, 0.5, 0.5, 1, 0, 0, 1, 0,

            0.5, 0.5, 0.5, 1, 0, 0, 1, 0,
            -0.5, 0.5, 0.5, 0, 0, 0, 1, 0,
            -0.5, 0.5, -0.5, 0, 1, 0, 1, 0
        )
        self.vertex_count = len(self.vertices) // 8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def update(self):
        glUseProgram(self.shader)
        angle = np.radians((20 * (pg.time.get_ticks() / 1000)) % 360)
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        # model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle,dtype=np.float32))
        model_transform = pyrr.matrix44.multiply(model_transform,
                                                 pyrr.matrix44.create_from_translation(vec=np.array(self.position),
                                                                                       dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model_transform)

    def draw(self):
        glUseProgram(self.shader)
        self.material.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class Material:
    def __init__(self, filepath):
        self.diffuseTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.diffuseTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}_diffuse.jpg").convert()
        image_width, image_height = image.get_rect().size
        img_data = pg.image.tostring(image, 'RGBA')
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.specularTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.specularTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}_specular.jpg").convert()
        image_width, image_height = image.get_rect().size
        img_data = pg.image.tostring(image, 'RGBA')
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.diffuseTexture)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.specularTexture)

    def destroy(self):
        glDeleteTextures(2, (self.diffuseTexture, self.specularTexture))


class Player:
    def __init__(self, position):
        self.position = np.array(position, dtype=np.float32)
        self.forward = np.array([0, 0, 0], dtype=np.float32)
        self.theta = 0
        self.phi = 0
        self.moveSpeed = 1
        self.global_up = np.array([0, 0, 1], dtype=np.float32)

    def move(self, direction, amount):
        walkDirection = (direction + self.theta) % 360
        self.position[0] += amount * self.moveSpeed * np.cos(np.radians(walkDirection), dtype=np.float32)
        self.position[1] += amount * self.moveSpeed * np.sin(np.radians(walkDirection), dtype=np.float32)

    def increment_direction(self, theta_increase, phi_increase):
        self.theta = (self.theta + theta_increase) % 360
        self.phi = min(max(self.phi + phi_increase, -89), 89)

    def update(self, shaders):
        camera_cos = np.cos(np.radians(self.theta), dtype=np.float32)
        camera_sin = np.sin(np.radians(self.theta), dtype=np.float32)
        camera_cos2 = np.cos(np.radians(self.phi), dtype=np.float32)
        camera_sin2 = np.sin(np.radians(self.phi), dtype=np.float32)
        self.forward[0] = camera_cos * camera_cos2
        self.forward[1] = camera_sin * camera_cos2
        self.forward[2] = camera_sin2

        right = pyrr.vector3.cross(self.global_up, self.forward)
        up = pyrr.vector3.cross(self.forward, right)
        lookat_matrix = pyrr.matrix44.create_look_at(self.position, self.position + self.forward, up, dtype=np.float32)
        for shader in shaders:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, lookat_matrix)
            glUniform3fv(glGetUniformLocation(shader, "cameraPos"), 1, self.position)


class Light:
    def __init__(self, shaders, colour, position, strength, index):
        self.model = CubeBasic(shaders[0], 0.1, 0.1, 0.1, colour[0], colour[1], colour[2])
        self.colour = np.array(colour, dtype=np.float32)
        self.shader = shaders[1]
        self.position = np.array(position, dtype=np.float32)
        self.strength = strength
        self.index = index

    def update(self):
        glUseProgram(self.shader)
        glUniform3fv(glGetUniformLocation(self.shader, f"lights[{self.index}].pos"), 1, self.position)
        glUniform3fv(glGetUniformLocation(self.shader, f"lights[{self.index}].color"), 1, self.colour)
        glUniform1f(glGetUniformLocation(self.shader, f"lights[{self.index}].strength"), self.strength)
        glUniform1i(glGetUniformLocation(self.shader, f"lights[{self.index}].enabled"), 1)

    def draw(self):
        self.model.draw(self.position)

    def destroy(self):
        self.model.destroy()


class CubeBasic:
    def __init__(self, shader, l, w, h, r, g, b):
        self.shader = shader
        glUseProgram(shader)
        # x, y, z, r, g, b
        self.vertices = (
            -l / 2, -w / 2, -h / 2, r, g, b,
            l / 2, -w / 2, -h / 2, r, g, b,
            l / 2, w / 2, -h / 2, r, g, b,

            l / 2, w / 2, -h / 2, r, g, b,
            -l / 2, w / 2, -h / 2, r, g, b,
            -l / 2, -w / 2, -h / 2, r, g, b,

            -l / 2, -w / 2, h / 2, r, g, b,
            l / 2, -w / 2, h / 2, r, g, b,
            l / 2, w / 2, h / 2, r, g, b,

            l / 2, w / 2, h / 2, r, g, b,
            -l / 2, w / 2, h / 2, r, g, b,
            -l / 2, -w / 2, h / 2, r, g, b,

            -l / 2, w / 2, h / 2, r, g, b,
            -l / 2, w / 2, -h / 2, r, g, b,
            -l / 2, -w / 2, -h / 2, r, g, b,

            -l / 2, -w / 2, -h / 2, r, g, b,
            -l / 2, -w / 2, h / 2, r, g, b,
            -l / 2, w / 2, h / 2, r, g, b,

            l / 2, w / 2, h / 2, r, g, b,
            l / 2, w / 2, -h / 2, r, g, b,
            l / 2, -w / 2, -h / 2, r, g, b,

            l / 2, -w / 2, -h / 2, r, g, b,
            l / 2, -w / 2, h / 2, r, g, b,
            l / 2, w / 2, h / 2, r, g, b,

            -l / 2, -w / 2, -h / 2, r, g, b,
            l / 2, -w / 2, -h / 2, r, g, b,
            l / 2, -w / 2, h / 2, r, g, b,

            l / 2, -w / 2, h / 2, r, g, b,
            -l / 2, -w / 2, h / 2, r, g, b,
            -l / 2, -w / 2, -h / 2, r, g, b,

            -l / 2, w / 2, -h / 2, r, g, b,
            l / 2, w / 2, -h / 2, r, g, b,
            l / 2, w / 2, h / 2, r, g, b,

            l / 2, w / 2, h / 2, r, g, b,
            -l / 2, w / 2, h / 2, r, g, b,
            -l / 2, w / 2, -h / 2, r, g, b
        )
        self.vertex_count = len(self.vertices) // 6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self, position):
        glUseProgram(self.shader)
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(model_transform,
                                                 pyrr.matrix44.create_from_translation(vec=position, dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


myApp = App()