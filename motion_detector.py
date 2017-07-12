import argparse
import imutils
import time
import cv2

line_point1 = (400,0)
line_point2 = (400,500)


#in this case above the line and inbetween the two points is considered in

ENTERED_STRING = "ENTERED_THE_AREA"
LEFT_AREA_STRING = "LEFT_THE_AREA"
NO_CHANGE_STRING = "NOTHIN_HOMEBOY"

LOWEST_CLOSEST_DISTANCE_THRESHOLD = 100

class Person:

    positions = []

    def __init__(self, position):
        self.positions = [position]

    def update_position(self, new_position):
        self.positions.append(new_position)
        if len(self.positions) > 100:
            self.positions.pop(0)


    def on_opposite_sides(self):
        return ((self.positions[-2][0] > line_point1[0] and self.positions[-1][0] <= line_point1[0])
                or (self.positions[-2][0] <= line_point1[0] and self.positions[-1][0] > line_point1[0]))

    def did_cross_line(self):
        if self.on_opposite_sides():
            if self.positions[-1][0] > line_point1[0]:
                return ENTERED_STRING
            else:
                return LEFT_AREA_STRING
        else:
            return NO_CHANGE_STRING

    def distance_from_last_x_positions(self, new_position, x):
        total = [0,0]
        z = x
        while z > 0:
            if (len(self.positions) > z):
                total[0] +=  self.positions[-(z+1)][0]
                total[1] +=  self.positions[-(z+1)][1]
            else:
                x -= 1
            z -= 1
        if total[0] < 1 or total[1] < 1:
            return abs(self.positions[0][0] - new_position[0]) + abs(self.positions[0][1] - new_position[1])
        total[0] = total[0] / x
        total[1] = total[1] / x

        return abs(new_position[0] - total[0]) + abs(new_position[1] - total[1])


def get_footage():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    args = vars(ap.parse_args())

    if args.get("video", None) is None:
        camera = cv2.VideoCapture(0)
        time.sleep(0.25)
        return camera

    else:
        return cv2.VideoCapture(args["video"])

def find_foreground_objects(background_model):
    thresh = cv2.threshold(background_model, 25, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=3)
    thresh = cv2.erode(thresh, None, iterations=10)
    cv2.imshow("Foreground Mfasdfaodel", thresh)


    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return cnts

def main():
    camera = get_footage()
    fgbg = cv2.createBackgroundSubtractorMOG2()
    frame_count = 0
    people_list = []
    inside_count = 5

    while True:

        (grabbed, frame) = camera.read()
        if not grabbed:
            break

        frame = imutils.resize(frame, width=500)

        frame_count += 1

        print(frame_count)

        filtered_frame = cv2.GaussianBlur(frame, (21, 21), 0)
        fgmask = fgbg.apply(filtered_frame)

        foreground_objects = find_foreground_objects(fgmask)

        for c in foreground_objects:
            if cv2.contourArea(c) < 5000:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            lowest_closest_distance = float("inf")
            rectangle_center = (((2 * x) + w)/2, ((2 * y) + h)/2)
            cv2.circle(frame, rectangle_center, 2, (0, 0, 255))
            closest_person_index = None


            for i in range(0, len(people_list)):
                if people_list[i].distance_from_last_x_positions(rectangle_center, 5) < lowest_closest_distance:
                    lowest_closest_distance = people_list[i].distance_from_last_x_positions(rectangle_center, 5)
                    closest_person_index = i
            if closest_person_index is not None:
                if lowest_closest_distance < LOWEST_CLOSEST_DISTANCE_THRESHOLD:
                    people_list[i].update_position(rectangle_center)
                    change = people_list[i].did_cross_line()
                    if change == ENTERED_STRING:
                        inside_count += 1
                    elif change == LEFT_AREA_STRING:
                        inside_count -= 1
                else:
                    new_person = Person(rectangle_center)
                    people_list.append(new_person)
            else:
                new_person = Person(rectangle_center)
                people_list.append(new_person)


        cv2.putText(frame, "Number of people inside: {}".format(inside_count), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.line(frame, line_point1, line_point2, (255, 0, 0), 2)
        cv2.imshow("Security Feed", frame)
        cv2.imshow("Foreground Model", fgmask)


        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

main()
