import pygame as pg
import pyrr
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader, GL_FALSE
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_2_0 import glUniformMatrix4fv
import numpy as np

width, height = 1000, 1000


class App:
    def __init__(self):
        # initialise pygame
        pg.init()
        pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        # initialise opengl
        glClearColor(0.5, 0.5, 0.1, 1)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        # self.triangle = Triangle(self.shader)
        self.rabbit = Rabbit(self.shader)
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        return shader

    def mainLoop(self):
        running = True
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        while (running):
            # check events
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                    break
                model_transform = self.control(model_transform)
                glUniformMatrix4fv(glGetUniformLocation(self.shader, "trans"), 1, GL_FALSE, model_transform)

            # refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            self.rabbit.draw(self.shader)
            pg.display.flip()

            # timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()

    def control(self, transform):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            return pyrr.matrix44.multiply(transform, pyrr.matrix44.create_from_translation(np.array([-0.05, 0, 0], dtype=np.float32)))
        if keys[pg.K_d]:
            return pyrr.matrix44.multiply(transform, pyrr.matrix44.create_from_translation(np.array([0.05, 0, 0], dtype=np.float32)))
        if keys[pg.K_w]:
            return pyrr.matrix44.multiply(transform, pyrr.matrix44.create_from_translation(np.array([0, 0.05, 0], dtype=np.float32)))
        if keys[pg.K_s]:
            return pyrr.matrix44.multiply(transform, pyrr.matrix44.create_from_translation(np.array([0, -0.05, 0], dtype=np.float32)))
        return transform

    def quit(self):
        self.rabbit.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class Rabbit:
    def __init__(self, shader):
        glUseProgram(shader)
        self.vertices = (
            # head
            -0.2, 0.6, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.6, 0.0, 0.0, 1.0, 0.0,
            -0.2, 0.4, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.4, 0.0, 0.0, 1.0, 0.0,
            # ear
            0.3, 0.6, 0.0, 0.0, 1, 0.0,
            0.15, 0.75, 0.0, 0.0, 1.0, 0.0,
            0.45, 0.75, 0.0, 0.0, 1.0, 0.0,
            # body
            0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            0.4, 0.0, 0.0, 0.0, 1.0, 0.0,
            0.4, -0.4, 0.0, 0.0, 1.0, 0.0,
            # leg
            0.0, -0.2, 0.0, 0.0, 1.0, 0.0,
            0.0, -0.4, 0.0, 0.0, 1.0, 0.0,
            0.2, -0.2, 0.0, 0.0, 1.0, 0.0,
            # front paws
            -0.15, 0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.15, 0.0, 0.0, 1.0, 0.0,
            0.0, -0.15, 0.0, 0.0, 1.0, 0.0,
        )

        self.black_lines_vertices = (
            # head
            -0.2, 0.6, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.6, 0.0, 0.0, 0.0, 0.0,
            -0.2, 0.4, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.4, 0.0, 0.0, 0.0, 0.0,
            # ear
            0.3, 0.6, 0.0, 0.0, 0.0, 0.0,
            0.15, 0.75, 0.0, 0.0, 0.0, 0.0,
            0.45, 0.75, 0.0, 0.0, 0.0, 0.0,
            # body
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.4, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.4, -0.4, 0.0, 0.0, 0.0, 0.0,
            # leg
            0.0, -0.2, 0.0, 0.0, 0.0, 0.0,
            0.0, -0.4, 0.0, 0.0, 0.0, 0.0,
            0.2, -0.2, 0.0, 0.0, 0.0, 0.0,
            # front paws
            -0.15, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.15, 0.0, 0.0, 0.0, 0.0,
            0.0, -0.15, 0.0, 0.0, 0.0, 0.0,
        )
        self.indicies = (
            # head
            0, 1, 2,
            1, 3, 2,
            # ear
            5, 6, 1,
            6, 4, 1,
            # body
            3, 8, 7,
            7, 8, 9,
            # leg
            12, 9, 11,
            10, 12, 11,
            # front paw
            13, 14, 15
        )

        self.lines_indicies = (
            # head
            0, 1,
            1, 3,
            3, 2,
            2, 0,
            # ear
            1, 5,
            5, 6,
            6, 4,
            4, 1,
            # body
            3, 7,
            7, 8,
            3, 8,
            # leg
            7, 9,
            8, 9,
            9, 12,
            11, 9,
            10, 12,
            10, 11,
            12, 11,
            # paw
            14, 13,
            13, 15,
            15, 7,
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.black_lines_vertices = np.array(self.black_lines_vertices, dtype=np.float32)
        self.indicies = np.array(self.indicies, dtype=np.uint32)
        self.lines_indicies = np.array(self.lines_indicies, dtype=np.uint32)

        # rabbit itself
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indicies.nbytes, self.indicies, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

        # black lines of rabbit
        self.vao1 = glGenVertexArrays(1)
        glBindVertexArray(self.vao1)

        self.vbo1 = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo1)
        glBufferData(GL_ARRAY_BUFFER, self.black_lines_vertices.nbytes, self.black_lines_vertices, GL_STATIC_DRAW)

        self.ebo1 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo1)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.lines_indicies.nbytes, self.lines_indicies, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self, shader):
        glUseProgram(shader)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indicies), GL_UNSIGNED_INT, None)
        glBindVertexArray(self.vao1)
        glDrawElements(GL_LINES, len(self.lines_indicies), GL_UNSIGNED_INT, None)

    def destroy(self):
        glDeleteVertexArrays(2, (self.vao, self.vao1,))
        glDeleteBuffers(3, (self.vbo, self.vbo1, self.ebo,))


myApp = App()
