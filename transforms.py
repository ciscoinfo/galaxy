

def transform(self, x, y):
    # return self.transform_2D(x, y)
    # return self.transform_perspective(x, y)
    #
    return self.transform_perspective_v2(x, y)


def transform_2D(self, x, y):
    return x, y


def transform_perspective(self, x1, y1):
    y2 = (y1 * self.perspective_point_y) / self.height
    if y2 > self.perspective_point_y:
        y2 = self.perspective_point_y

    x2 = (self.perspective_point_x - x1) * (y2 / self.perspective_point_y) + x1

    return x2, y2


def transform_perspective_v2(self, x1, y1):
    line_y = (y1 * self.perspective_point_y) / self.height
    if line_y > self.perspective_point_y:
        line_y = self.perspective_point_y

    dx = x1 - self.perspective_point_x
    dy = self.perspective_point_y - line_y
    factor_y = dy / self.perspective_point_y
    factor_y = pow(factor_y, 2)

    offset_x = dx * factor_y

    x2 = self.perspective_point_x + offset_x
    y2 = self.perspective_point_y - factor_y * self.perspective_point_y

    return x2, y2