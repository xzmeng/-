from matplotlib import pyplot as plt


def plot_bar(tags, nums):
    plt.bar(tags, nums)
    plt.show()


def plot_pie(tags, nums):
    plt.pie(nums, labels=tags, autopct='%1.1f%%', shadow=False, startangle=90)
    plt.show()



if __name__ == '__main__':
    names = ['group_a', 'group_b', 'group_c']
    values = [1, 10, 100]
    plot_pie(names, values)